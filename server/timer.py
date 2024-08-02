import asyncio
import time

CHECK_FREQUENCY = .1

def create_timer(duration: float):
	now = time.time()
	return {
		"start": now,
		"end": now + duration,
		"pause_start": None,
		"active": True,
		"num_running": 0
	}

async def run_timer(duration: float, checker: callable , callback: callable, parameters: dict, callback_params: dict = None, purpose = None):
	proceed = True
	while (proceed):
		await asyncio.sleep(duration)
		#  catch if the room is empty/deleted but timer is still going (gracefully close the timer)
		try:
			proceed, duration = checker(time.time(), **parameters)
		except TypeError:
			break

	if (duration == 0):
		if (purpose):
			print(purpose)
		if (callback_params is None):
			await callback(**parameters)
		else:
			await callback(**callback_params)