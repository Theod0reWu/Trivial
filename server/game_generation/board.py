import google.generativeai as genai
import numpy as np
import os
import random

from . import prompt
from . import boarditem
from . import gemini

from .prompt import CategoryPromptGenerator, AnswerPromptGenerator, CluePromptGenerator, CategoryAndClueGenerator, TopicGenerator
from .boarditem import BoardItem
from .gemini import (get_and_parse_categories, get_and_parse_answers, get_and_parse_clues, get_and_parse_catans, 
	get_and_parse_ast, get_and_parse_ast_async, get_similarity, verify_answer)

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

CATEGORY_LEVEL = 2

def remove_parenthesis(data: str):
	if ("(" in data):
		return data[:data.index("(")]
	return data

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
		self.extra_ans = min(self.clues_per_category * 8, 100)
		if (given_categories is None):
			self.given_categories = []
		else:
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
		self.answer_json = TopicGenerator(os.path.join(os.path.dirname(__file__),'prompts/answer_json.txt'))
		# self.title_json = TopicGenerator(os.path.join(os.path.dirname(__file__),'prompts/category_title_json.txt'))
		self.title_json = TopicGenerator(os.path.join(os.path.dirname(__file__),'prompts/title_no_ans_json.txt'))

	def clear_picked(self):
		self.picked = [[False for i in range(self.clues_per_category)] for i in range(self.num_categories)]

	def clear_data(self):
		self.category_titles = []
		self.all_categories = []
		self.items = []

	INVALID_SECTIONS = ['See also', 'References', 'Works cited', 'Further reading', 'External links']
	def get_valid_page_sections(page):
		sections = []
		for section in page.sections:
			if (section not in Board.INVALID_SECTIONS):
				sections.append(section)
		return sections

	def info_from_page(page, summary = True, num_sections = 1):
		valid_sections = Board.get_valid_page_sections(page)
		section_names = random.sample(valid_sections, min(len(valid_sections), num_sections))
		info = ""
		for i in range(len(section_names)):
			section_name = section_names[i]
			section_text = page.section(section_name)
			if ( section_text is not None):
				info += section_text + " "
		return  info + page.summary

	def get_wikipedia_page(self, ans, category, alt_answers):
		# search wikipedia for a relevant page (if the answer is not specific enough try it with the category)
		num_search_results = 3
		search = None
		while (search is None):
			try:
				search = wikipedia.search(ans + " (" + category + ")", results = num_search_results)
			except wikipedia.exceptions.WikipediaException as e:
				print(e)
		if (len(search) == 0):
			search = wikipedia.search(ans, results = num_search_results)

		backup_page, backup_ans = None, None
		for e in range(num_search_results):
			result = search[e]

			# get the wikipedia page
			page = None
			try:
				page = wikipedia.page(result, auto_suggest = False)
				if (not verify_answer(ans, page.title, threshold = .93)):
					if (len(alt_answers) > 0):
						return self.get_wikipedia_page(alt_answers.pop(), category, alt_answers)
					else:
						ans = remove_parenthesis(page.title)
			except wikipedia.exceptions.DisambiguationError as ex:
				# currently the disambiguation error will just select the next best option from suggestions
				# This is only done from the first result
				if (e == 0):
					backup_page = wikipedia.page(ex.options[0], auto_suggest = False)
					backup_ans = remove_parenthesis(backup_page.title)
				continue

			#backup is chosen if none of the search results resulted in pages
			if (page is not None):
				return ans, page
		return backup_ans, backup_page

	def get_wikipedia_info(self, answers, category, alt_answers = []):
		information = []
		for i in range(len(answers)):
			answers[i], page = self.get_wikipedia_page(answers[i], category, alt_answers)
			information.append("For the answer: " + answers[i] + "the associated information is: " + "\"" + Board.info_from_page(page) + "\"")
			
		return answers, information

	def generate_answers(self, model, category_tree):
		num_to_get = min(self.clues_per_category * 8, 100)
		answers = []
		for i in range(self.num_categories):
			ans_output = get_and_parse_ast(model, self.answer_json.generate_prompt(num=num_to_get, category=self.all_categories[i]))
			if (ans_output is None):
				self.all_categories[i] = category_tree.get_random_topic(model, CATEGORY_LEVEL)
				ans_output = get_and_parse_ast(model, self.answer_json.generate_prompt(num=num_to_get, category=self.all_categories[i]))
			answers.append(random.sample(ans_output, self.clues_per_category))
		return answers

	def generate_answers_single_category(self, model, category):
		ans_output = get_and_parse_ast(model, self.answer_json.generate_prompt(num=self.extra_ans, category=category))
		if (ans_output is None):
			return ans_output
		ans_idx = random.sample([i for i in range(len(ans_output))], self.clues_per_category)
		return [ans_output[i] for i in ans_idx], [ans_output[i] for i in range(len(ans_output)) if i not in ans_idx]

	def generate_clues(self, model, answers, information):
		clue_prompt = self.clue_gen_json.generate_prompt(num = self.clues_per_category, answers = ", ".join(answers), information = "\n\n".join(information))
		clues = get_and_parse_ast(model, clue_prompt)
		return clues

	def get_a_category(self,  model, category_tree, given_categories=None, column_at=None):
		category = None
		if (column_at is not None and given_categories is not None and column_at < len(given_categories)):
			category = given_categories[column_at]
		else:
			category = category_tree.get_random_topic(model, CATEGORY_LEVEL)
		return category

	def generate_column(self, model, category_tree, given_categories, column_at):
		# first generate the category
		category = self.get_a_category(model, category_tree, given_categories, column_at)

		# next generate answers for the category
		answers, alt_answers = self.generate_answers_single_category(model, category)
		while (answers is None): # if category is bad generate a new category
			category = self.get_a_category(model, category_tree)
			answers, alt_answers = self.generate_answers_single_category(model, category)

		# gather info from wikipedia
		answers, information = self.get_wikipedia_info(answers, category, alt_answers)

		# generate the clues 
		max_tries = 1
		clues = None
		for i in range(max_tries):
			clues = self.generate_clues(model, answers, information)
			if (clues is not None):
				break
		if (clues is None or answers is None):
			return self.generate_column(model, category_tree, given_categories, column_at)
		return category, answers, clues


	def refresh(self, category_tree, model, min_price = 200, price_incr = 200):
		self.clear_picked()
		self.clear_data()

		given_categories = None
		if (self.given_categories is not None):
			given_categories = random.sample(self.given_categories, k=min(len(self.given_categories), self.num_categories))
		
		for column_at in range(self.num_categories):
			category, answers, clues = self.generate_column(model, category_tree, given_categories, column_at)

			title = get_and_parse_ast(model, self.title_json.generate_prompt(category=category, answers=", ".join(answers)))
			if (title is None):
				title = category
			self.category_titles.append(title)

			items = []
			for e in range(self.clues_per_category):
				items.append(BoardItem(clues[e], answers[e], min_price + price_incr * e))
			self.items.append(items)

	def refresh_v2(self, category_tree, model, min_price = 200, price_incr = 200):
		self.clear_picked()
		self.items = []

		# generate categories
		if (len(self.given_categories) < self.num_categories):
			self.all_categories = [category_tree.get_random_topic(model, CATEGORY_LEVEL) for i in range(self.num_categories - len(self.given_categories))]
			self.all_categories.extend(self.given_categories)
		else:
			self.all_categories = random.sample(self.given_categories, k=self.num_categories)
		print(self.all_categories)

		# generate answers
		answers = self.generate_answers(model, category_tree)
		print(answers)

		for i in range(self.num_categories):
			title = get_and_parse_ast(model, self.title_json.generate_prompt(category=self.all_categories[i], answers=", ".join(answers[i])))
			print(title)
			self.category_titles.append(title)

			ans = answers[i]
			ans, information = self.get_wikipedia_info(ans, self.all_categories[i])

			max_tries = 3
			clues = None
			for i in range(max_tries):
				clues = self.generate_clues(model, ans, information)
				if (clues is not None):
					break
			print("clues:", clues)

			items = []
			for e in range(self.clues_per_category):
				items.append(BoardItem(clues[e], ans[e], min_price + price_incr * e))
			self.items.append(items)

	def refresh_v1(self, category_tree, model, fact_model = None, min_price = 200, max_price = 1000):
		self.clear_picked()
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1)) if self.clues_per_category > 1 else 0
		self.items = []

		# generate categories (old way: only generates the categories)
		# self.all_categories = [category_tree.get_random_topic(model, 3) for i in range(self.num_categories)]

		self.all_categories = []
		answers = []
		for i in range(self.num_categories):
			# problem: there could be less children then clues_per_category (error is thrown in this case)
			output = category_tree.get_n_random_topics(model, 3, self.clues_per_category)
			answers.append(output["children"])
			self.all_categories.append(output["parent"])
		print(self.all_categories)
		print(answers)

		for i in range(self.num_categories):
			# figure out a better way to get the titles
			self.category_titles.append(self.all_categories[i])

			ans = answers[i]
			ans, information = self.get_wikipedia_info(ans, self.all_categories[i])

			clue_prompt = self.clue_gen_json.generate_prompt(num = self.clues_per_category, answers = ", ".join(ans), information = "\n\n".join(information))
			clues = []
			if (fact_model is None):
				clues = get_and_parse_ast(model, clue_prompt)
			else:
				clues = get_and_parse_ast(fact_model, clue_prompt)
			print(clues)

			items = []
			for e in range(self.clues_per_category):
				items.append(BoardItem(clues[e], ans[e], min_price + price_incr * e))
			self.items.append(items)
	
	def refresh_old(self, model, fact_model = None, min_price = 200, max_price = 1000):
		'''
			Expects a model without response_mime_type = "application/json".
			Fact model is for the option to provide a different model for clue generation
		'''
		self.clear_picked()
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1)) if self.clues_per_category > 1 else 0
		self.items = []

		# category_prompt = self.category_gen.generate_prompt(num = self.num_categories)
		# categories = get_and_parse_categories(model, category_prompt)
		# print(categories)
		catans_prompt = self.catans_gen.generate_prompt(num_categories = self.num_categories, num_answers = self.clues_per_category)
		categories, all_answers = get_and_parse_catans(model, catans_prompt)

		self.all_categories = [i[0] for i in categories]
		print(categories, all_answers)
		
		at = 0
		for category in categories:
			self.category_titles.append(category[1])

			# answer_prompt = self.answer_gen.generate_prompt(num = self.clues_per_category, singular = category[0], plural = category[1])
			# answers = get_and_parse_answers(model, answer_prompt)
			# print(answers)
			answers = all_answers[at]

			answers, information = self.get_wikipedia_info(answers, categories)

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
			at+=1

	async def refresh_async(self, category_tree, model, fact_model = None, min_price = 200, max_price = 1000):
		'''
			Performs an asynchronous refresh of the board.

			Excepts model to have reponse type json.
		'''
		self.clear_picked()
		price_incr = round((max_price - min_price) / (self.clues_per_category - 1)) if self.clues_per_category > 1 else 0
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
			for i in range(self.clues_per_category):
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
		# print("board:", self.items, self.num_categories, self.clues_per_category)
		data = {}
		for i in range(self.num_categories):
			key = str(i)
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