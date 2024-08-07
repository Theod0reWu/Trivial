from .board import Board
from .category_generator import CategoryTree

from enum import Enum
import os
import asyncio
import random
import traceback

import google.generativeai as genai
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class GameState(Enum):
    PREGAME = 'pregame'
    LOADING = 'loading'
    BOARD = 'board'
    CLUE = 'clue'
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
	MAX_RETRIES = 4
	def __init__(self, player_ids, num_players: int, num_categories: int, num_clues: int, given_categories: list[str] = [], use_json = True):
		super(Game, self).__init__()
		self.num_players = num_players
		self.num_categories = num_categories
		self.num_clues = num_clues
		self.num_finished = 0

		self.board = Board(num_categories, num_clues, given_categories)

		self.player_cash = {i:0 for i in player_ids}
		self.answered = []#{i:False for i in player_ids}
		self.player_ids = player_ids
		self.picker = random.choice(player_ids) # who's turn it is to pick
		self.picking = {"category_idx": "", "clue_idx": ""} # last clue picked

		self.state = GameState.BOARD
		if (use_json):
		    self.config = genai.types.GenerationConfig(
		        candidate_count = 1,
		        response_mime_type = "application/json",
		    )
		else:
		    self.config = genai.types.GenerationConfig(
		        candidate_count = 1,
		    )
		# self.model = genai.GenerativeModel('gemini-1.5-pro', generation_config = self.config)
		self.model = genai.GenerativeModel('gemini-1.5-flash', generation_config = self.config)

		self.category_tree = CategoryTree()

	def create_new_board(self, num_categories: int, num_clues: int):
		self.board = Board(num_categories, num_clues)

	def generate_board(self):
		count = 0
		while(count < Game.MAX_RETRIES):
			try:
				self.board.refresh(self.category_tree, self.model)
				break
			except Exception as e:
				print(e)
				print(traceback.format_exc())
				count += 1

			# try with custom categories twice
			if (count > 2):
				self.board.given_categories = []
		# self.board.refresh(self.category_tree, self.model)

	async def generate_board_async(self):
	    await self.board.refresh_async(self.category_tree, self.model)

	def to_dict(self):
	    data = {
	        # "num_players": self.num_players,
	        "player_cash": self.player_cash,

	        "num_finished": self.num_finished,
	        "num_categories": self.num_categories,
	        "num_clues": self.num_clues,
	        "category_titles": self.board.category_titles,

	        "picked": array_to_dict(self.board.picked),
	        'picking': self.picking,
	        "picker": self.picker,

	        "answered": self.answered,
	        'answering': None,

	        "state": self.state.value
	    }
	    data["board_data"] = self.board.to_dict()
	    return data

	def test_dict(player_ids):
	    return {
	        # 'num_players': 1, 
	        'player_cash': {i:0 for i in player_ids}, 
	        "num_finished": 0,
	        'num_categories': 2, 
	        'num_clues': 3, 
	        'category_titles': ['baseball', 'emotional intelligence'], 
	        
	        'picked': {'0': {'0': False, '1': False, '2': False}, '1': {'0': False, '1': False, '2': False}}, 
	        'picker': random.choice(player_ids), 
	        'picking': {"category_idx": "", "clue_idx": ""},
	        
	        'answered': [],
	        'answering': None,

	        'state': 'board', 
	        'board_data': 
	        {
	            '0': [
	                {'clue': 'This term is a process of administration that involves the management of resources for organizations of varying types including businesses, nonprofits, and government bodies.', 
	                'answer': 'managers',
	                'price': 100
	                }, 
	                {'clue': "This statistic in baseball and softball is used to measure the number of wins and losses credited to a pitcher and is based on the pitcher's performance in a game and the official scorer's judgment. There are specific rules that govern the attribution of a win, loss, or a no-decision. The number of decisions a pitcher accumulates has been on a gradual decline since the early 1900s as the evolution of baseball has led to a reliance on specialized pitchers.", 
	                'answer': 'pitching records',
	                'price': 200
	                }, 
	                {'clue': 'This part of baseball history revolves around the career of a player whose dominant pitching performance led to his selection as the starting pitcher for the National League in the 2024 All-Star Game, making him only the fifth rookie to achieve this distinction.', 
	                'answer': 'mlb history',
	                'price': 400
	                }
	            ], 
	            '1': [
	                {'clue': "It is a concept that describes how individuals within a society become aware of the common ground that connects them and their shared identity, which can lead to social unity and shared goals. It's a key concept in Marxism, where it's argued that economic relations shape social consciousness.", 
	                'answer': 'social awareness',
	                'price': 100
	                }, 
	                {'clue': 'It is a business process that involves managing and analyzing customer interactions across various communication channels, aiming to improve customer satisfaction, retention, and sales growth. It is a multi-billion dollar industry with a large global market.', 
	                'answer': 'relationship management',
	                'price': 200
	                }, 
	                {'clue': "It is a form of organizational management where employees have a significant degree of control over their work processes and the organization's operations. It's a defining feature of socialism and has been advocated by various socialist and anarchist movements. It's often linked to concepts like employee ownership and worker cooperatives.", 
	                'answer': 'self-management',
	                'price': 400
	                }
	            ]
	        }
	    }

	def pick(self, category, clue):
		return self.board[category][clue]

	def who_picks(self):
		return self.player_ids[picker]

