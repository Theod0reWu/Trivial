import google.generativeai as genai
import numpy as np

import os

from prompt import CategoryPromptGenerator, AnswerPromptGenerator, CluePromptGenerator, CategoryAndClueGenerator
from board import Board
from gemini import get_and_parse_catans

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

config = genai.types.GenerationConfig(
    candidate_count = 1,
    temperature = 1.2,
    top_p = 1,
    # top_k = 40,
)

fact_config = genai.types.GenerationConfig(
    candidate_count = 1,
    temperature = .2,
)



model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)

prompt = CategoryAndClueGenerator().generate_prompt(num_categories = 6, num_answers = 5)
print(prompt, "\n")

categories = {}
answers = {}

num_tests = 10

for i in range(num_tests):
	c, a = get_and_parse_catans(model, prompt)

	for cat in c:
		if (cat[0] not in categories):
			categories[cat[0]] = 1
		else:
			categories[cat[0]] += 1

	for ans_list in a:
		for ans in ans_list:
			if (ans not in answers):
				answers[ans] = 1
			else:
				answers[ans] += 1

# print(categories)
print(dict(sorted(categories.items(), key=lambda item: item[1])))
print()

# print(answers)
print(dict(sorted(answers.items(), key=lambda item: item[1])))