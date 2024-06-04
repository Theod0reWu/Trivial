from board import Board


class Game(object):
	"""docstring for Game"""
	def __init__(self, num_players, num_categories, num_clues):
		super(Game, self).__init__()
		self.num_players = num_players
		self.num_categories = num_categories
		self.num_clues = num_clues

		self.board = Board(num_categories, num_clues)
		self.player_cash = [0 for i in range(num_players)]
		self.player_ids = [None for i in range(num_players)]
		self.picker = 0

	def run(self):
		self.board.refresh()
		while (not self.board.clear()):
			# ask for a player to pick a board spot

			# relay the clue and answer to all players

			# answer checking

			# update money

			return

	def pick(self, category, clue):
		return self.board[category][clue]

	def who_picks(self):
		return self.player_ids[picker]

