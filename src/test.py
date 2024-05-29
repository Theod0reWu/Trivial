import google.generativeai as genai
import numpy as np

import os

from prompt import CategoryPromptGenerator, AnswerPromptGenerator
from clues import Clue, parse_content

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel('gemini-1.0-pro-latest')

category_gen = CategoryPromptGenerator()
prompt = category_gen.generate_prompt(num = 6)

response = model.generate_content(prompt)
print(response.text)

categories = response.text.split("\n")
print(categories[0].split(","))
first = categories[0].split(",")

answer_gen = AnswerPromptGenerator()
prompt = answer_gen.generate_prompt(num = 5, singular = first[0][2:], plural = first[1])

response = model.generate_content(prompt)
print(response.text)

for i in range(5):
	ans = response.text.split("\n")
	print(ans[i][7:] + " " + first[0][2:])
	search = wikipedia.search(ans[i][7:], results = 3)
	print(search)
	search = wikipedia.search(ans[i][7:] + " " + first[0][2:], results = 3)
	print(search)
	result = search[0]
	page = wikipedia.page(result, auto_suggest = False)
	print(page)