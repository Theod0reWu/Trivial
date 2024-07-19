import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError
import google.generativeai as genai

def get_wikipedia_info(answers, category):
	information = []
	for i in range(len(answers)):
		# search wikipedia for a relevant page (if the answer is not specific enough try it with the category)
		num_search_results = 3
		search = wikipedia.search(answers[i], results = num_search_results)
		if (len(search) == 0):
			search = wikipedia.search(answers[i] + " " + categories[i], results = num_search_results)

		backup_page, backup_ans = None, None
		for e in range(num_search_results):
			result = search[e]

			# get the wikipedia page
			page = None
			try:
				page = wikipedia.page(result, auto_suggest = False)
			except wikipedia.exceptions.DisambiguationError as e:
				# currently the disambiguation error will just select the next best option from suggestions
				# This is only done from the first result
				if (i == 0):
					backup_page = wikipedia.page(e.options[0], auto_suggest = False)
					backup_ans = e.options[0]
				continue

			#backup is chosen if none of the search results resulted in pages
			if (page is not None):
				information.append("Answer: " + answers[i] + "\n Information: " + "\"" + page.summary + "\"")
				break

		if (len(information) < i):
			print("testing")
			information.append("Answer: " + backup_ans + "\n Information: " + "\"" + backup_page.summary + "\"")
			answers[i] = backup_ans
	return answers, information

print(get_wikipedia_info(["imagine"], "music"))
