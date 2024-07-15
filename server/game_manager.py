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

		game = Game(len(room["curr_connections"]),num_categories, num_clues)
		game.generate_board()

		data = game.to_dict()
		print(data)
		room_ref.update(data)

	def start_game(self, room_id: str):
		room_ref = self.rooms.document(room_id)
		room_ref.update({"state": GameState.BOARD.value})

	def get_game_state(self, room_id: str):
		room_ref = self.rooms.document(room_id)
		return room_ref.get().to_dict()["state"]

	# Create a callback on_snapshot function to capture changes
	def on_snapshot(doc_snapshot, changes, read_time):
	    for doc in doc_snapshot:
	        print(f"Received document snapshot: {doc.id}")
	    callback_done.set()