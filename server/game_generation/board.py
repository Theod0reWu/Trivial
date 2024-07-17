import google.generativeai as genai
import numpy as np
import os

from . import prompt
from . import boarditem
from . import gemini

from .prompt import CategoryPromptGenerator, AnswerPromptGenerator, CluePromptGenerator, CategoryAndClueGenerator
from .boarditem import BoardItem
from .gemini import get_and_parse_categories, get_and_parse_answers, get_and_parse_clues, get_and_parse_catans, get_and_parse_ast_async

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

class Board(object):
	"""
		The board class containing one trivia board

		Specify how many categories (columns) and how many clues per category (rows)
		Optional: specify any categories you wish to be included.
	"""
	def __init__(self, categories, clues_per_category, given_categories = None):
		super(Board, self).__init__()
		self.num_categories = categories
		self.clues_per_category = clues_per_category
		self.given_categories = given_categories

		self.category_titles = [] # title of category for board display
		self.all_categories = [] # actual category

		# each item is one clue/answer on the jeopardy board
		self.items = [[None for i in range(clues_per_category)] for i in range(categories)]
		# picked represents if a board item has been picked already
		self.picked = [[False for i in range(clues_per_category)] for i in range(categories)]

		# old prompt system
		self.category_gen = CategoryPromptGenerator()
		self.answer_gen = AnswerPromptGenerator()
		self.catans_gen = CategoryAndClueGenerator()
		self.clue_gen = CluePromptGenerator()

		#json prompts
		self.answer_gen_json = AnswerPromptGenerator(make_json=True)
		self.clue_gen_json = CluePromptGenerator(make_json=True)

	def clear_picked(self):
		self.picked = [[False for i in range(self.clues_per_category)] for i in range(self.num_categories)]

	def get_wikipedia_info(self, answers):
		information = []
		for i in range(self.clues_per_category):
			# search wikipedia for a relevant page
			search = wikipedia.search(answers[i], results = 3)
			if (len(search) == 0):
				search = wikipedia.search(answers[i] + " " + category[0], results = 3)
			result = search[0]

			# get the wikipedia page
			page = None
			try:
				page = wikipedia.page(result, auto_suggest = False)
			except wikipedia.exceptions.DisambiguationError as e:
				# page = wikipedia.page(e.options[0], auto_suggest = False)
				try:
					page = wikipedia.page(e.options[0])
					answers[i] = e.options[0]
				except wikipedia.exceptions.DisambiguationError:
					print("Failed generation")
					return None

			# currently only uses the summary for information
			information.append("Answer: " + answers[i] + "\n Information: " + "\"" + page.summary + "\"")
		return answers, information

	def refresh(self):
		self.clear_picked()
		# use category tree
	
	def refresh_old(self, model, fact_model = None, min_price = 200, max_price = 1000):
		'''
			Expects a model without response_mime_type = "application/json".
			Fact model is for the option to provide a different model for clue generation
		'''
		self.clear_picked()
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1))
		self.items = []

		# category_prompt = self.category_gen.generate_prompt(num = self.num_categories)
		# categories = get_and_parse_categories(model, category_prompt)
		# print(categories)
		catans_prompt = self.catans_gen.generate_prompt(num_categories = self.num_categories, num_answers = self.clues_per_category)
		categories, all_answers = get_and_parse_catans(model, catans_prompt)

		self.all_categories = [i[0] for i in categories]
		print(categories, all_answers)
		
		for category in categories:
			self.category_titles.append(category[1])

			# answer_prompt = self.answer_gen.generate_prompt(num = self.clues_per_category, singular = category[0], plural = category[1])
			# answers = get_and_parse_answers(model, answer_prompt)
			# print(answers)
			answers = all_answers[at]

			answers, information = self.get_wikipedia_info(answers)

			# get clues based on info + answer
			clue_prompt = self.clue_gen.generate_prompt(num = self.clues_per_category, answers = ", ".join(answers), information = "\n\n".join(information))
			clues = []
			if (fact_model is None):
				clues = get_and_parse_clues(model, clue_prompt)
			else:
				clues = get_and_parse_clues(fact_model, clue_prompt)
			print(clues)

			items = []
			for i in range(len(answers)):
				items.append(BoardItem(clues[i], answers[i], min_price + price_incr * i))
			self.items.append(items)

	async def refresh_async(self, category_tree, model, fact_model = None, min_price = 200, max_price = 1000):
		'''
			Performs an asynchronous refresh of the board.

			Excepts model to have reponse type json.
		'''
		self.clear_picked()
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1))
		self.items = []

		# generate categories (old way: only generates the categories)
		# self.all_categories = [await category_tree.get_random_topic_async(model, 3) for i in range(self.num_categories)]

		self.all_categories = []
		answers = []
		for i in range(self.num_categories):
			# problem: there could be less children then clues_per_category (error is thrown in this case)
			output = await category_tree.get_n_random_topics_async(model, 3, self.clues_per_category)
			answers.append(output["children"])
			self.all_categories.append(output["parent"])
		print(self.all_categories)
		print(answers)

		for i in range(self.num_categories):
			# figure out a better way to get the titles
			self.category_titles.append(self.all_categories[i])

			ans = answers[i]
			ans, information = self.get_wikipedia_info(ans)

			clue_prompt = self.clue_gen_json.generate_prompt(num = self.clues_per_category, answers = ", ".join(ans), information = "\n\n".join(information))

			clues = []
			if (fact_model is None):
				clues = await get_and_parse_ast_async(model, clue_prompt)
			else:
				clues = await get_and_parse_ast_async(fact_model, clue_prompt)
			print(clues)

			items = []
			for i in range(len(answers)):
				items.append(BoardItem(clues[i], ans[i], min_price + price_incr * i))
			self.items.append(items)


	def __str__(self):
		output = "\t\t".join(self.category_titles) + "\n"
		output += '\n'
		for row in range(self.clues_per_category):
			for cat in range(self.num_categories):
				output += self.items[cat][row].clue + "\t\t"
		output += '\n'
		for row in range(self.clues_per_category):
			for cat in range(self.num_categories):
				output += self.items[cat][row].answer + "\t\t"
		return output

	def to_dict(self):
		print("board:", self.items, self.num_categories, self.clues_per_category)
		data = {}
		for i in range(self.num_categories):
			key = "cat_" + str(i + 1)
			data[key] = []
			for e in range(self.clues_per_category):
				if (self.items[i][e]):
					data[key].append(self.items[i][e].to_dict())
				else:
					data[key].append(None)
		return data

	def __getitem__(self, category : int):
		return self.items[category]

	def clear(self):
		for i in range(self.num_categories):
			for e in range(self.clues_per_category):
				if (not self.picked[i][e]):
					return False
		return True