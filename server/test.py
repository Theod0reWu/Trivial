import google.generativeai as genai
import os

from game_generation.board import Board
from game_generation.game import Game

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

# model = genai.GenerativeModel('gemini-1.0-pro-latest')
model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)
fact_model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)


game = Game(1, 2, 3)
game.generate_board()

print(game.to_dict())
