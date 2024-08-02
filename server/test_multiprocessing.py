from game_manager import GameManager
import multiprocessing
import asyncio

game_manager = GameManager()

async def create_game():

    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool, heavy_duty, input)