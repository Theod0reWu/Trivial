import google.generativeai as genai
import numpy as np

import os
import typing_extensions as typing

from prompt import CategoryPromptGenerator, AnswerPromptGenerator, CategoryAndClueGenerator, TopicGenerator
from board import Board
from gemini import get_and_parse_topics, get_and_parse_ast
from category_generator import CategoryGenerator, CategoryTree

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

config = genai.types.GenerationConfig(
    candidate_count = 1,
    response_mime_type = "application/json",
)

model = genai.GenerativeModel('gemini-1.5-pro', generation_config = config)
# prompt = TopicGenerator('./prompts/topics_json.txt').generate_prompt(category = "history")
# output = get_and_parse_ast(model, prompt)
# print(output)

cat_tree = CategoryTree()

print(cat_tree.get_random_topic(model, 2))
print(cat_tree.get_random_topic(model, 2))
print(cat_tree.get_random_topic(model, 2))

cat_tree.save_checkpoint()

print(cat_tree)