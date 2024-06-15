import google.generativeai as genai
import numpy as np

import os

from prompt import PromptGenerator, CategoryPromptGenerator, AnswerPromptGenerator, CluePromptGenerator, CategoryAndClueGenerator
from boarditem import BoardItem
from gemini import get_and_parse_categories, get_and_parse_answers, get_and_parse_clues, get_and_parse_catans, get_and_parse_ast
from category_generator import CategoryTree

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

		self.category_titles = []
		self.all_categories = []
		# each item is one clue/answer on the jeopardy board
		self.items = [[None for i in range(clues_per_category)] for i in range(categories)]
		# picked represents if a board item has been picked already
		self.picked = [[False for i in range(clues_per_category)] for i in range(categories)]

		self.cat_tree = CategoryTree()

		# json
		self.answer_json = PromptGenerator("./prompts/answers_json.txt")
		self.clue_json = PromptGenerator("./prompts/clue_gen_json.txt")

		# prompt system
		self.answer_gen = AnswerPromptGenerator()
		self.catans_gen = CategoryAndClueGenerator()
		self.clue_gen = CluePromptGenerator()

	def clear_picked(self):
		self.picked = [[False for i in range(self.clues_per_category)] for i in range(self.num_categories)]

	def refresh(self, model, fact_model = None, min_price = 200, max_price = 1000):
		self.clear_picked()
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1))
		self.items = []
		
		categories = [self.cat_tree.get_random_topic(model, 2)[0] for i in range(self.num_categories)]

		self.all_categories = categories
		at = 0
		for category in categories:
			self.category_titles.append(category)

			answer_prompt = self.answer_json.generate_prompt(num = self.clues_per_category, category = category)
			answers = get_and_parse_ast(model, answer_prompt)

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
					try:
						page = wikipedia.page(e.options[0])
						answers[i] = e.options[0]
					except wikipedia.exceptions.DisambiguationError:
						print("Failed generation")
						return None
						# page = wikipedia.page(e.options[0], auto_suggest = False)

				# currently only uses the summary for information
				information.append("Answer: " + answers[i] + "\n Information: " + "\"" + page.summary + "\"")

			# get clues based on info + answer
			clue_prompt = self.clue_json.generate_prompt(num = self.clues_per_category, answers = ", ".join(answers), information = "\n\n".join(information))
			clues = []
			if (fact_model is None):
				clues = get_and_parse_ast(model, clue_prompt)
			else:
				clues = get_and_parse_ast(fact_model, clue_prompt)
			print(clues)

			items = []
			for i in range(len(answers)):
				items.append(BoardItem(clues[i], answers[i], min_price + price_incr * i))

			self.items.append(items)
			at += 1
	
	def refresh_old(self, model, fact_model = None, min_price = 200, max_price = 1000):
		self.clear_picked()
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1))
		self.items = []
		
		# pure prompt category and answer generation
		catans_prompt = self.catans_gen.generate_prompt(num_categories = self.num_categories, num_answers = self.clues_per_category)
		categories, all_answers = get_and_parse_catans(model, catans_prompt)

		self.all_categories = [i[0] for i in categories]
		at = 0
		for category in categories:
			self.category_titles.append(category[1])

			# answer_prompt = self.answer_gen.generate_prompt(num = self.clues_per_category, singular = category[0], plural = category[1])
			# answers = get_and_parse_answers(model, answer_prompt)
			# print(answers)
			answers = all_answers[at]

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
					page = wikipedia.page(e.options[0])

				# currently only uses the summary for information
				information.append("Answer: " + answers[i] + "\n Information: " + "\"" + page.summary + "\"")

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
			at += 1

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

	def __getitem__(self, category : int):
		return self.clues[category]

	def clear(self):
		for i in range(self.num_categories):
			for e in range(self.clues_per_category):
				if (not self.picked[i][e]):
					return False
		return True