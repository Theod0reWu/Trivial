import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InternalServerError
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import time
import ast
import asyncio

import numpy as np

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

'''
	Returns the first candidate response from the model 
'''
def get_response(model, prompt):
	response = None
	while response == None:
		try:
			response = model.generate_content(prompt, safety_settings = safety_settings)
		except ResourceExhausted:
			time.sleep(1)

	try:
		# print(response.candidates[0].content.parts[0].text)
		return response.candidates[0].content.parts[0].text
	except Exception as e:
		print("gemini error:",e)
		print(prompt)
		print(response)
		print("feedback:",response.prompt_feedback, "|")

async def get_response_async(model, prompt):
	response = None
	while response == None:
		try:
			# async can generate the following error: google.api_core.exceptions.InternalServerError: 500 An internal error has occurred.
			# response = await model.generate_content_async(prompt)
			response = model.generate_content(prompt)
		except (ResourceExhausted, InternalServerError):
			await asyncio.sleep(1)

	try:
		# print(prompt)
		# print(response.candidates[0].content.parts[0].text)
		return response.candidates[0].content.parts[0].text
	except Exception as e:
		print("gemini error:",e)
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
	var = None
	try: 
		var = ast.literal_eval(response)
	except ValueError as e:
		print(e)
		print("Error with this prompt:", prompt)
		print("Prompt gave this response:", response)
	return var

async def get_and_parse_ast_async(model, prompt):
	response = await get_response_async(model, prompt)
	var = ast.literal_eval(response)
	return var

def get_similarity(answer: str, guess:str):
	guess_emb = genai.embed_content(
			    model="models/embedding-001",
			    content=guess,
			    task_type="SEMANTIC_SIMILARITY")
	ans_emb = genai.embed_content(
			    model="models/embedding-001",
			    content=answer,
			    task_type="SEMANTIC_SIMILARITY")
	return np.dot(ans_emb['embedding'], guess_emb['embedding'])

def levenshtein_distance(token1, token2):
	# source: https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/
    distances = np.zeros((len(token1) + 1, len(token2) + 1))

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2
        
    a = 0
    b = 0
    c = 0
    
    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if (token1[t1-1] == token2[t2-1]):
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]
                
                if (a <= b and a <= c):
                    distances[t1][t2] = a + 1
                elif (b <= a and b <= c):
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1
    return distances[len(token1)][len(token2)]

def verify_answer(answer, guess, threshold = .94, distance = 1):
	answer = answer.lower()
	guess = guess.lower()
	return levenshtein_distance(answer, guess) <= distance or get_similarity(answer, guess) >= threshold