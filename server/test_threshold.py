from game_generation.gemini import get_similarity, verify_answer, levenshtein_distance

tests = [
	("neo", "neo-noir", False), 
	("manager", "managers", True),
	("dreadnought", "dreadnought (ship)", True),
	("deadnought", "super-dreadnought", False),
	("contract", "contract law", True),
	("tort", "Tort", True),
	("transistor", "Field-effect Transistor", False),
	("agile methodology", "agile software developement", True),
	("pitching record", "pitching records", True),
	("zigguarat", "Ziggurat", True)
]

for i in tests:
	print(i)
	print(get_similarity(i[0], i[1]))
	print(levenshtein_distance(i[1], i[0]))
	print()