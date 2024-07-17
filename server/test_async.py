import google.generativeai as genai
import os
import asyncio

from game_generation.game import Game

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])



config = genai.types.GenerationConfig(
    candidate_count = 1,
    response_mime_type = "application/json",
    # temperature = .5
)
model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)

game = Game(1, 2, 3)

asyncio.run(game.generate_board_async())

print(game.to_dict())
