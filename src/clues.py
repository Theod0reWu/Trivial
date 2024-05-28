import google.generativeai as genai
import numpy as np

class Clue(object):
	"""
		
	"""
	def __init__(self, clue, answer):
		super(Clue, self).__init__()
		self.clue = clue.strip()
		self.answer = answer.strip()

		self.ans_embedding = genai.embed_content(
		    model="models/embedding-001",
		    content=self.answer,
		    task_type="SEMANTIC_SIMILARITY")
	
	def guess_distance(self, guess) -> float:
		guess_emb = genai.embed_content(
		    model="models/embedding-001",
		    content=guess,
		    task_type="SEMANTIC_SIMILARITY")

		return np.dot(self.ans_embedding['embedding'], guess_emb['embedding'])

	def check_answer(self, guess, threshold = .95) -> bool:
		return self.guess_distance(guess) >= threshold

def parse_content(content):
	lines = content.split("\n")
	clues = []
	
	q_at = -1
	x = 0
	while (x < len(lines)):
		if (lines[x][:9] == "Question:"):
			q_at = x
		if (lines[x][:7] == "Answer:" and q_at != -1):
			clues.append(Clue(lines[q_at][9:], lines[x][7:]))
			q_at = -1
		x+=1
	return clues