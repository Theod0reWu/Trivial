import asyncio
import time

CHECK_FREQUENCY = .1

def create_timer(duration: float):
	now = time.time()
	return {
		"start": now,
		"end": now + duration,
		"pause_start": None,
		"active": True
	}

async def run_timer(duration: float, callback: callable, parameters):
	proceed = True
	while (proceed):
		await asyncio.sleep(duration)
		proceed, duration = callback(time.time(), **parameters)
		