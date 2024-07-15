import google.generativeai as genai
import numpy as np

class BoardItem(object):
	"""
		Stores each clue and answer
	"""
	def __init__(self, clue, answer, price):
		super(BoardItem, self).__init__()
		self.clue = clue.strip()
		self.answer = answer.strip()
		self.price = price

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

	def to_dict(self):
		return {
			"clue": self.clue,
			"answer": self.answer
		}

	def __str__(self):
		return self.clue + "\n" + self.answer + "\n"