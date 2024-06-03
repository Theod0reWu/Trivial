import google.generativeai as genai
import numpy as np

import os

from prompt import CategoryPromptGenerator, AnswerPromptGenerator, CluePromptGenerator
from boarditem import BoardItem
from gemini import get_and_parse_categories, get_and_parse_answers, get_and_parse_clues

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
		self.categories = categories
		self.clues_per_category = clues_per_category
		self.given_categories = given_categories

		self.category_titles = []
		self.all_categories = []
		self.items = [[None for i in range(clues_per_category)] for i in range(categories)]
		self.category_gen = CategoryPromptGenerator()
		self.answer_gen = AnswerPromptGenerator()
		self.clue_gen = CluePromptGenerator()
	
	def refresh(self, model, min_price = 200, max_price = 1000):
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1))

		category_prompt = self.category_gen.generate_prompt(num = self.categories)
		categories = get_and_parse_categories(model, category_prompt)
		print(categories)

		self.all_categories = [i[1] for i in categories]
		at = 0
		for category in categories:
			self.category_titles.append(category[2])

			answer_prompt = self.answer_gen.generate_prompt(num = self.clues_per_category, singular = category[0], plural = category[1])
			answers = get_and_parse_answers(model, answer_prompt)
			print(answers)

			information = []
			for i in range(self.clues_per_category):
				# search wikipedia for a relevant page
				search = wikipedia.search(answers[i], results = 1)
				if (len(search) == 0):
					search = wikipedia.search(answers[i] + " " + category[0], results = 3)
				result = search[0]

				# get the wikipedia page
				page = None
				try:
					page = wikipedia.page(result, auto_suggest = False)
				except DisambiguationError as e:
					page = wikipedia.page(e.options[0], auto_suggest = False)

				# currently only uses the summary for information
				information.append("\"" + page.summary + "\"")

			# get clues based on info + answer
			clue_prompt = self.clue_gen.generate_prompt(num = self.clues_per_category, answers = ", ".join(answers), information = "\n".join(information))
			clues = get_and_parse_clues(model, clue_prompt)

			items = []
			for i in range(len(answers)):
				items.append(BoardItem(clues[i], answers[i], min_price + price_incr * i))

			self.items[at] = items
			at += 1

	def __str__(self):
		output = "\t\t".join(self.category_titles) + "\n"
		output += '\n'
		for row in range(self.clues_per_category):
			for cat in range(self.categories):
				output += self.items[cat][row].clue + "\t\t"
		output += '\n'
		for row in range(self.clues_per_category):
			for cat in range(self.categories):
				output += self.items[cat][row].answer + "\t\t"
		return output

	def __getitem__(self, category : int):
		return self.clues[category]