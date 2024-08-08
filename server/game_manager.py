from firebase_init import db
from firebase_admin import firestore

import sys
import time
import asyncio
import multiprocessing
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor

from game_generation.game import Game, GameState
from game_generation.gemini import get_similarity, verify_answer
from timer import create_timer, CHECK_FREQUENCY

BUZZ_IN_TIMER_NAME = "buzz_in_timer"
ANSWER_TIMER_NAME = "answer_timer"

class GameManager(object):
    """
        Responsible for storing game states and info in the database

        game states:
            pregame
                -before game starts
            board
                -players should be looking at the board
            clue
                -players should be looking at a clue
    """
    def __init__(self, ):
        super(GameManager, self).__init__()
        self.rooms = db.collection('Rooms')

    def init_game(self, room_id: str, num_categories: int, num_clues: int) -> None:
        '''
            Expects room_id to already exist in firebase from room_manager
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()

        game = Game(room_data["curr_connections"], len(room_data["curr_connections"]),num_categories, num_clues)
        game.generate_board()
        try:
            data = game.to_dict()
        except:
            print(game.board.items)
        # data = Game.test_dict(room["curr_connections"])
        
        room_ref.update(data)

    async def init_game_async(self, room_id: str, num_categories: int, num_clues: int, given_categories: list[str]) -> None:
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()
        game = Game(room_data["curr_connections"], len(room_data["curr_connections"]),num_categories, num_clues, given_categories)

        process = multiprocessing.Process(target=game.generate_board())
        process.start()

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, process.join)
        data = game.to_dict()

        room_ref.update(data)

    def start_game(self, room_id: str) -> None:
        self.set_game_state(room_id, GameState.BOARD)

    def end_game(self, room_id: str) -> None:
        self.set_game_state(room_id, GameState.DONE)

    def get_game_state(self, room_id: str) -> str:
        room_ref = self.rooms.document(room_id)
        return room_ref.get().to_dict()["state"]
    
    def set_game_state(self, room_id: str, state: GameState) -> None:
        room_ref = self.rooms.document(room_id)
        room_ref.update({"state": state.value})

    def get_board_info(self, room_id: str) -> dict:
        '''
            Returns the category titles and prices of the board
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()
        titles = room_data["category_titles"]
        prices = [i["price"] for i in room_data["board_data"]["0"]]
        # print(room_data)
        return {
            "category_titles": titles, 
            "prices": prices, 
            "num_categories": room_data["num_categories"], 
            "num_clues": room_data["num_clues"]
        }

    def get_player_cash(self, room_id: str, player_ids: list[str]) -> list[int]:
        '''
            player_id: list of session ids of players in room_id
            returns ordered list of player cash (int)
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()["player_cash"]
        return [room_data[i] for i in player_ids]

    def get_picker(self, room_id: str) -> str:
        '''
            Returns the session_id of the picker
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()
        return room_data["picker"]

    def pick(self, session_id: str, room_id:str, category_idx: str, clue_idx: str) -> str | None:
        '''
            Picks the clue located at category_idx and clue_idx
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()

        # ensure session_id of the caller matches the picker
        if (session_id != room_data["picker"]):
            return None

        picked = room_data["picked"][category_idx][clue_idx]
        if (picked):
            print("cannot pick board spot", category_idx, ",", clue_idx, "due to it already being picked.")
            return None
        else:
            clue = room_data["board_data"][category_idx][int(clue_idx)]["clue"]
            room_ref.update({
                "picked."+category_idx + "." + clue_idx: True,
                "picking.category_idx":category_idx, "picking.clue_idx": clue_idx, 
                "state": GameState.CLUE.value,
                "answered": []
                })
            return clue

    def init_buzz_in_timer(self, room_id: str, duration: float) -> any:
        return self.init_timer(room_id, BUZZ_IN_TIMER_NAME, duration)

    def init_answer_timer(self, room_id: str, duration: float) -> any:
        return self.init_timer(room_id, ANSWER_TIMER_NAME, duration)

    def init_timer(self, room_id: str, timer_name: str, duration: float) -> any:
        room_ref = self.rooms.document(room_id)
        timer = create_timer(duration)
        room_ref.update({timer_name: timer})
        return timer

    def check_buzz_in_timer(self, time: float, room_id:str) -> tuple[bool, int]:
        return self.check_timer(time, room_id, BUZZ_IN_TIMER_NAME)

    def check_answer_timer(self, time: float, room_id:str) -> tuple[bool, int]:
        return self.check_timer(time, room_id, ANSWER_TIMER_NAME)

    def check_timer(self, time: float, room_id: str, timer_name: str) -> tuple[bool, int]:
        '''
            Two cases:
            1. timer is active (no pause), continue the timer until the end
            2. timer is paused, wait for the timer to unpause, then continue the timer 
        '''
        room_ref = self.rooms.document(room_id)
        timer_data = room_ref.get().to_dict()[timer_name]

        if (timer_data["active"] and timer_data["num_running"] == 0):
            if (time >= timer_data["end"]):
                return False, 0
            else:
                # this should never happen
                return True, time - timer_data["end"]
        else:
            # timer is currently paused (check if unpaused)
            room_ref.update({timer_name+".num_running": firestore.Increment(-1)})
            return False, 1

    def get_timer(self, room_id: str, timer_name: str) -> str:
        room_ref = self.rooms.document(room_id)
        return room_ref.get()[timer_name]

    def pause_buzz_in_timer(self, room_id: str) -> None:
        '''
            Increments the number of running timers by one in expectation what one will be started
        '''
        room_ref = self.rooms.document(room_id)
        room_ref.update({
            BUZZ_IN_TIMER_NAME + ".active": False, 
            BUZZ_IN_TIMER_NAME + ".pause_start": time.time(),
            BUZZ_IN_TIMER_NAME + ".num_running": firestore.Increment(1)
            })

    def restart_buzz_in_timer(self, room_id: str) -> int:
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()
        timer_data = room_data[BUZZ_IN_TIMER_NAME]
        duration =timer_data["end"] - timer_data["pause_start"]
        room_ref.update({
            BUZZ_IN_TIMER_NAME + ".active": True, 
            BUZZ_IN_TIMER_NAME + ".end": duration + time.time()
            })
        return duration

    def handle_buzz_in(self, room_id:str, session_id: str) -> bool:
        '''
            Returns true is the session_id player successfully buzzed-in for a clue in room_id
            and false otherwise
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()

        # ensure player is in the room and that the player hasn't answered yet
        if (not session_id in room_data["curr_connections"] or session_id in room_data["answered"] or room_data["answering"] is not None):
            return False
        room_data["answered"].append(session_id)
        room_ref.update({"answered": room_data["answered"], "answering": session_id})
        self.set_game_state(room_id, GameState.ANSWERING)
        return True

    def reset_clue(self, room_id: str) -> None:
        room_ref = self.rooms.document(room_id)
        room_ref.update({"answered": []})

    def get_picked_clues(self, room_id: str, room_data = None) -> tuple[list[list[bool]], dict]:
        if (room_data is None):
            room_ref = self.rooms.document(room_id)
            room_data = room_ref.get().to_dict()
        return room_data["picked"], room_data

    def stop_answering(self, room_id: str) -> None:
        room_ref = self.rooms.document(room_id)
        room_ref.update({"answering": None})
        self.set_game_state(room_id, GameState.CLUE)
    
    def handle_answer(self, room_id: str, session_id: str, answer: str, threshold = .94) -> bool:
        '''
            Ensures that the person who buzzed in is the one answering

            If the player can answer and is correct:
                increases "player_cash"
                removes the "picked" clue
                assignes the answering player as "picker"
            In both cases the answering timer is set to inactive and "answering" marked as None
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()
        picking = room_data["picking"]

        if (session_id != room_data["answering"]):
            raise ValueError("Wrong user attempting to answer")
        if (picking["category_idx"] == "" or picking["clue_idx"] == ""):
            raise ValueError("Not in the correct phase, not clue picked")

        board_item = room_data["board_data"][picking["category_idx"]][int(picking["clue_idx"])]

        right_answer = board_item["answer"]

        # similarity_score = get_similarity(right_answer, answer) >= threshold
        # correct = similarity_score >= threshold
        correct = verify_answer(right_answer, answer, threshold)

        if (correct):
            room_ref.update({
                "player_cash." + session_id: room_data["player_cash"][session_id] + board_item["price"],
                "picking.category_idx": "",
                "picking.clue_idx": "",
                "picker": session_id,
                "answering": None,
                ANSWER_TIMER_NAME + ".active": False
                })
        else:
            room_ref.update({
                # "player_cash." + session_id: room_data["player_cash"][session_id] - board_item["price"],
                ANSWER_TIMER_NAME + ".active": False,
                "answering": None
                })
        return correct

    def get_correct_ans(self, room_id: str, room_data = None) -> tuple[str, dict]:
        if (room_data is None):
            room_ref = self.rooms.document(room_id)
            room_data = room_ref.get().to_dict()
        picking = room_data["picking"]
        board_item = room_data["board_data"][picking["category_idx"]][int(picking["clue_idx"])]
        return board_item["answer"], room_data

    def deduct_points(self, room_id: str, session_id: str) -> bool:
        '''
            Deducts points from the picked question from the given session_id

            Also returns true if everyone has buzzed in.
        '''
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()
        picking = room_data["picking"]
        board_item = room_data["board_data"][picking["category_idx"]][int(picking["clue_idx"])]
        room_ref.update({
                "player_cash." + session_id: room_data["player_cash"][session_id] - board_item["price"]
                })
        return len(room_data["curr_connections"]) == len(room_data["answered"])

    def check_game_over(self, room_id: str) -> bool:
        room_ref = self.rooms.document(room_id)
        room_data = room_ref.get().to_dict()
        room_data["num_finished"] += 1
        if (room_data["num_finished"] == room_data["num_categories"]*room_data["num_clues"]):
            return True
        else:
            room_ref.update(room_data)
            return False