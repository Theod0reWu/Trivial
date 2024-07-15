from . import board
from .board import Board
from enum import Enum

import os
import google.generativeai as genai
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class GameState(Enum):
    PREGAME = 'pregame'
    BOARD = 'board'
    BUZZ_IN = 'buzz_in'
    ANSWERING = 'answering'
    DONE = 'done'

def array_to_dict(arr):
	if not (type(arr) == type([])):
		return arr
	data = {}
	for i in range(len(arr)):
		data[str(i)] = array_to_dict(arr[i])
	return data

class Game(object):
	"""
		
	"""
	def __init__(self, num_players: int, num_categories: int, num_clues: int):
		super(Game, self).__init__()
		self.num_players = num_players
		self.num_categories = num_categories
		self.num_clues = num_clues

		self.board = Board(num_categories, num_clues)

		self.player_cash = [0 for i in range(num_players)]
		self.player_ids = [None for i in range(num_players)]
		self.picker = -1 # who's turn it is to pick

		self.state = GameState.BOARD
		self.config = genai.types.GenerationConfig(
		    candidate_count = 1,
		    # response_mime_type = "application/json",
		)

		self.model = genai.GenerativeModel('gemini-1.5-pro', generation_config = self.config)

	def generate_board(self):
		self.board.refresh(self.model)

	def run(self):
		self.board.refresh()
		while (not self.board.clear()):
			# ask for a player to pick a board spot

			# relay the clue and answer to all players

			# answer checking

			# update money

			return

	def to_dict(self):
		data = {
			"num_players": self.num_players,
			"player_cash": self.player_cash,

			"num_categories": self.num_categories,
			"num_clues": self.num_clues,
			"category_titles": self.board.category_titles,
			"picked": array_to_dict(self.board.picked),

			"picker": self.picker,
			"state": self.state.value
		}
		data["board_data"] = self.board.to_dict()
		return data

	def pick(self, category, clue):
		return self.board[category][clue]

	def who_picks(self):
		return self.player_ids[picker]

