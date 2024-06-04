import google.generativeai as genai
import numpy as np

import os

from prompt import CategoryPromptGenerator, AnswerPromptGenerator, CluePromptGenerator
from board import Board

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel('gemini-1.0-pro-latest')

board = Board(1, 5)
board.refresh(model)
print(board)

