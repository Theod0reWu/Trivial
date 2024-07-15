import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

import time
import ast
import asyncio

'''
	Returns the first candidate response from the model 
'''
def get_response(model, prompt):
	response = None
	while response == None:
		try:
			response = model.generate_content(prompt)
		except ResourceExhausted:
			time.sleep(.5)

	try:
		# print(response.candidates[0].content.parts[0].text)
		return response.candidates[0].content.parts[0].text
	except:
		print(response)
		print(response.prompt_feedback)

async def get_response_async(model, prompt):
	response = None
	while response == None:
		try:
			response = model.generate_content(prompt)
		except ResourceExhausted:
			await asyncio.sleep(.5)

	try:
		# print(response.candidates[0].content.parts[0].text)
		return response.candidates[0].content.parts[0].text
	except:
		print(response)
		print(response.prompt_feedback)

'''
	the response from the model, should be sentences separated by "\n". Sometimes extra ones are added.
	removes the extra newlines and leading/trailing spaces
'''
def split_and_clean(response, split_token = "\n"):
	temp = response.split(split_token)
	output = []
	for i in temp:
		if (len(i) > 0):
			output.append(i.strip())
	return output


'''
	Expects a prompt from CategoryPromptGenerator

	Returns a 2d list of all categories
'''
def get_and_parse_categories(model, prompt):
	response = get_response(model, prompt)
	categories = [i.split(",") for i in split_and_clean(response)]
	# remove "-"
	for i in range(len(categories)):
		categories[i][0] = categories[i][0][2:].strip()
	return categories

'''
	Expects a prompt from AnswerPromptGenerator

	Returns a list of answers
'''
def get_and_parse_answers(model, prompt):
	response = get_response(model, prompt)
	# remove "Answer:"
	answers = [i[7:].strip() for i in split_and_clean(response)]
	return answers

'''
	Expects a prompt from CluePromptGenerator

	Returns a list of clues
'''
def get_and_parse_clues(model, prompt):
	response = get_response(model, prompt)
	lines = split_and_clean(response)
	clues = []

	for line in lines:
		if (line[:5] == "Clue:"):
			clues.append(line[5:])
	return clues

'''
	Expects a prompt from CategoryAndClueGenerator

	returns a list of categories and a list of clues
	the list of categories contains ["category", "category title"]
'''
def get_and_parse_catans(model, prompt):
	response = get_response(model, prompt)
	lines = split_and_clean(response)
	answers = []
	categories = []
	for line in lines:
		if (line[:9] == "Category:"):
			categories.append(split_and_clean(line[9:], ','))
		elif (line[:8] == 'Answers:'):
			answers.append(split_and_clean(line[8:], ';'))
	return categories, answers

'''
	Expects a prompt from TopicGenerator

	returns a list of topics
'''
def get_and_parse_topics(model, prompt):
	response = get_response(model, prompt)
	lines = split_and_clean(response)
	topics = []
	try:
		for line in lines:
			tokens = split_and_clean(line, ".")
			topics.append(tokens[1])
	except:
		print("Error parsing")
		print(lines)
		raise ValueError
	return topics

def get_and_parse_ast(model, prompt):
	response = get_response(model, prompt)
	var = ast.literal_eval(response)
	return var

async def get_and_parse_ast_async(model, prompt):
	response = await get_response(model, prompt)
	var = ast.literal_eval(response)
	return var