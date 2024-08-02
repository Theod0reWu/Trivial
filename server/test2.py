import google.generativeai as genai
import numpy as np

import os
import typing_extensions as typing

from prompt import CategoryPromptGenerator, AnswerPromptGenerator, CategoryAndClueGenerator
from board import Board
from gemini import get_and_parse_topics, get_and_parse_ast

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

class Recipe(typing.TypedDict):
    recipe_name: str

class Category(typing.TypedDict):
    title : str
    answers: list[str]

config = genai.types.GenerationConfig(
    candidate_count = 1,
    temperature = 1,
    top_k = 5,
    response_mime_type = "application/json",
    # response_schema = list[Category]
)

model = genai.GenerativeModel('gemini-1.5-pro', generation_config = config)
# model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)
prompt = CategoryAndClueGenerator("./prompts/category_and_answers_json.txt").generate_prompt(num_categories = 5, num_answers = 2)

response = model.generate_content(prompt)
output = response.candidates[0].content.parts[0].text
print(output)

import ast
var=ast.literal_eval(output)
print(var)