import google.generativeai as genai

'''
	Returns the first candidate response from the model 
'''
def get_response(model, prompt):
	response = model.generate_content(prompt)
	try:
		return response.candidates[0].content.parts[0].text
	except e:
		print(e)
		print(response.promptFeedback)
		
'''
	the response from the model, should be sentences separated by "\n". Sometimes extra ones are added.
	removes the extra newlines and leading/trailing spaces
'''
def split_and_clean(response, split_token = "\n"):
	temp = response.split("\n")
	output = []
	for i in temp:
		if (len(i) > 0):
			output.append(i.strip())
	return output


'''
	Expects a prompt from CategoryPromptGenerator

	Returns a 2d list of all categories
'''
def get_and_parse_categories(model, prompt):
	response = get_response(model, prompt)
	categories = [i.split(",") for i in split_and_clean(response)]
	# remove "-"
	for i in range(len(categories)):
		categories[i][0] = categories[i][0][2:].strip()
	return categories

'''
	Expects a prompt from AnswerPromptGenerator

	Returns a list of answers
'''
def get_and_parse_answers(model, prompt):
	response = get_response(model, prompt)
	# remove "Answer:"
	answers = [i[7:].strip() for i in split_and_clean(response)]
	return answers

'''
	Expects a prompt from CluePromptGenerator

	Returns a list of clues
'''
def get_and_parse_clues(model, prompt):
	response = get_response(model, prompt)
	lines = split_and_clean(response)
	clues = []

	for line in lines:
		if (line[:5] == "Clue:"):
			clues.append(Clue(lines[x][5:], answers[a_at]))
	return clues