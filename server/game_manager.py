from firebase_init import db
from firebase_admin import firestore
import sys

from game_generation.game import Game, GameState

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

	# Create a callback on_snapshot function to capture changes
	def on_snapshot(doc_snapshot, changes, read_time):
	    for doc in doc_snapshot:
	        print(f"Received document snapshot: {doc.id}")
	    callback_done.set()