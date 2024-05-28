import google.generativeai as genai
import numpy as np

import os

from prompt import CategoryGenerator
from clues import Clue, parse_content

default_prompt_path = './prompts/clue_based.txt' 
default_prompt_path = './prompts/default.txt'

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel('gemini-1.0-pro-latest')

movies_gen = CategoryGenerator(default_prompt_path, "movies")
prompt = movies_gen.generate_question_prompt(5)
# print(prompt)

def sentence_similarity(s1, s2):
	e1 = genai.embed_content(
	    model="models/embedding-001",
	    content=s1,
	    task_type="SEMANTIC_SIMILARITY")

	e2 = genai.embed_content(
	    model="models/embedding-001",
	    content=s2,
	    task_type="SEMANTIC_SIMILARITY")

	return np.dot(e1['embedding'], e2['embedding'])


response = model.generate_content(prompt)
# print(response.text)

clues = parse_content(response.text)
for i in clues:
	print(i.clue)
	guess = input("Your answer: ")

	if (i.check_answer(guess)):
		print("Correct!")
	else:
		print("Incorrect! We were looking for:", i.answer)
	print()