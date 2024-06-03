from board import Board


class Game(object):
	"""docstring for Game"""
	def __init__(self, num_players, num_categories, num_clues):
		super(Game, self).__init__()
		self.num_players = num_players
		self.num_categories = num_categories
		self.num_clues = num_clues

		self.Board(num_categories, num_clues)