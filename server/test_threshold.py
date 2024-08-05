from game_generation.gemini import get_similarity

tests = [
	("neo", "neo-noir", False), 
	("manager", "managers", True),
	("dreadnought", "dreadnought (ship)", True),
	("deadnought", "super-dreadnought", False),
	("contract", "contract law", True),
	("tort", "Tort", True),
	("transistor", "Field-effect Transistor", False)
]

for i in tests:
	print(i)
	print(get_similarity(i[0], i[1]))
	print()