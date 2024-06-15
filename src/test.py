import google.generativeai as genai
import numpy as np

import os

from prompt import CategoryPromptGenerator, AnswerPromptGenerator, CluePromptGenerator
from board import Board

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

config = genai.types.GenerationConfig(
    candidate_count = 1,
    temperature = 1,
    # top_p = 1
    top_k = 20,
)

fact_config = genai.types.GenerationConfig(
    candidate_count = 1,
    temperature = .2,
)

config = genai.types.GenerationConfig(
    candidate_count = 1,
    response_mime_type = "application/json",
)

# model = genai.GenerativeModel('gemini-1.0-pro-latest')
model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)
fact_model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)

board = Board(1, 3)
board.refresh(model)
print(board)

