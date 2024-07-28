from firebase_init import db
from firebase_admin import firestore

import sys
import time

from game_generation.game import Game, GameState
from timer import create_timer, CHECK_FREQUENCY

BUZZ_IN_TIMER_NAME = "buzz_in_timer"
ANSWER_TIMER_NAME = "answer_timer"

class GameManager(object):
	"""
		Responsible for storing game states and info in the database
	"""

	keys = ["state", "categories", "clues"]
	def __init__(self, ):
		super(GameManager, self).__init__()
		self.rooms = db.collection('Rooms')

	def init_game(self, room_id: str, room, num_categories, num_clues):
		'''
			Expects room_id to already exist in firebase from room_manager
		'''
		room_ref = self.rooms.document(room_id)

		game = Game(room["curr_connections"], len(room["curr_connections"]),num_categories, num_clues)
		# game.generate_board()
		# data = game.to_dict()
		data = Game.test_dict(room["curr_connections"])

		print(num_categories, num_clues)
		print(data)
		room_ref.update(data)

	def start_game(self, room_id: str):
		room_ref = self.rooms.document(room_id)
		room_ref.update({"state": GameState.BOARD.value})

	def get_game_state(self, room_id: str):
		room_ref = self.rooms.document(room_id)
		return room_ref.get().to_dict()["state"]

	def get_board_info(self, room_id: str):
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

	def get_player_cash(self, room_id: str, player_ids: list[str]):
		'''
			player_id: list of session ids of players in room_id
			returns ordered list of player cash
		'''
		room_ref = self.rooms.document(room_id)
		room_data = room_ref.get().to_dict()["player_cash"]
		return [room_data[i] for i in player_ids]

	def get_picker(self, room_id: str):
		'''
			Returns the session_id of the picker
		'''
		room_ref = self.rooms.document(room_id)
		room_data = room_ref.get().to_dict()
		return room_data["picker"]

	def pick(self, session_id: str, room_id:str, category_idx: str, clue_idx: str):
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
			room_ref.update({"picked."+category_idx + "." + clue_idx: True})
			room_ref.update({"picking.category_idx":category_idx, "picking.clue_idx": clue_idx});
			return clue

	def init_buzz_in_timer(self, room_id: str, duration: float):
	    return self.init_timer(room_id, BUZZ_IN_TIMER_NAME, duration)

	def init_answer_timer(self, room_id: str, duration: float):
		return self.init_timer(room_id, ANSWER_TIMER_NAME, duration)

	def init_timer(self, room_id: str, timer_name: str, duration: float):
		room_ref = self.rooms.document(room_id)
		timer = create_timer(duration)
		room_ref.update({timer_name: timer})
		return timer

	def check_buzz_in_timer(self, time: float, room_id:str):
		return self.check_timer(time, room_id, BUZZ_IN_TIMER_NAME)

	def check_answer_timer(self, time: float, room_id:str):
		return self.check_timer(time, room_id, ANSWER_TIMER_NAME)

	def check_timer(self, time: float, room_id: str, timer_name: str):
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
	            return True, time - timer_data["end"]
	    else:
	        # timer is currently paused (check if unpaused)
	        # use onSnapshot for this to change it (currently uses too any calls
	        print("timer over")
	        room_ref.update({timer_name+".num_running": firestore.Increment(-1)})
	        return False, 1

	def get_timer(self, room_id: str, timer_name: str):
	     room_ref = self.rooms.document(room_id)
	     return room_ref.get()[timer_name]

	def pause_buzz_in_timer(self, room_id: str):
	    room_ref = self.rooms.document(room_id)
	    room_ref.update({
	    	BUZZ_IN_TIMER_NAME + ".active": False, 
	    	BUZZ_IN_TIMER_NAME + ".pause_start": time.time(),
	    	BUZZ_IN_TIMER_NAME + ".num_running": firestore.Increment(1)
	    	})

	def restart_buzz_in_timer(self, room_id: str):
		room_ref = self.rooms.document(room_id)
		timer_data = room_ref.get().to_dict()[BUZZ_IN_TIMER_NAME]
		duration =timer_data["end"] - timer_data["pause_start"]
		room_ref.update({
		    BUZZ_IN_TIMER_NAME + ".active": True, 
		    BUZZ_IN_TIMER_NAME + ".end": duration + time.time(),
		    })
		return duration

	def handle_buzz_in(self, room_id:str, session_id: str):
		room_ref = self.rooms.document(room_id)
		room_data = room_ref.get().to_dict()

		# ensure player is in the room and that the player hasn't answered yet
		if (not session_id in room_data["curr_connections"] or session_id in room_data["answered"]):
			return False
		room_data["answered"].append(session_id)
		room_ref.update({"answered": room_data["answered"]})
		return True

	def reset_clue(self, room_id: str):
		room_ref = self.rooms.document(room_id)
		room_ref.update({"answered": []})

	# Create a callback on_snapshot function to capture changes
	def on_snapshot(doc_snapshot, changes, read_time):
	    for doc in doc_snapshot:
	        print(f"Received document snapshot: {doc.id}")
	    callback_done.set()