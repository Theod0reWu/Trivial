from gemini import get_and_parse_topics, get_and_parse_ast
from prompt import TopicGenerator

import random
import os

class CategoryTree(object):
	"""
		Tree data structure for containing categories

		A depth of 3 is ideal for generating broad enough categories for the purposes of trivia. (might even be to specific in some cases)
	"""
	def __init__(self, start = "general", load_path =  os.path.join(os.path.dirname(__file__), 'category_data/')):
		super(CategoryTree, self).__init__()
		self.root = CategoryNode(0, None, "general")
		self.total_topics = 1
		self.depth = 1

		# self.prompt_gen = TopicGenerator('./prompts/topics_json.txt') # for non-json return format
		self.prompt_gen = TopicGenerator( os.path.join(os.path.dirname(__file__), 'prompts/topics_json.txt'))

		self.load_path = load_path
		if (load_path is not None):
			self.load_checkpoint()

	'''
		Level should start at 1
	'''
	def get_random_topic(self, model, level):
		level_at = 0
		node_at = self.root
		while (level_at < level):
			new = node_at.make_children(model, self.prompt_gen)
			self.total_topics += new
			if (new > 0 and node_at.level + 1 > self.depth):
				self.depth = node_at.level + 1
			node_at = random.choice(node_at.children)
			level_at += 1
		return node_at.topic

	def node_savename(self, topic : str):
		return os.path.join(self.load_path, topic + ".txt").replace(" ", "_")	

	def load_checkpoint(self):
		stack = [self.root]
		while len(stack) > 0:
			at = stack.pop()
			fname = self.node_savename(at.topic)
			if (os.path.isfile(fname)):
				data = None
				with open(fname) as f:
					data = f.read().strip().split("\n")
				at.add_children(data)
				for c in at.children:
					stack.append(c)

	def save_checkpoint(self):
		stack = [self.root]
		while len(stack) > 0:
			at = stack.pop()
			fname = self.node_savename(at.topic)
			if (at.has_children() and not os.path.isfile(fname)):
				at.save(fname)

			for c in at.children:
				stack.append(c)

	def __repr__(self):
		return str(self.root)

class CategoryNode(object):
	"""
		
	"""
	def __init__(self, level, parent, topic):
		super(CategoryNode, self).__init__()
		self.parent = parent
		self.level = level
		self.topic = topic

		self.children = []

	def has_children(self):
		return len(self.children) != 0

	def add_children(self, child_topics):
		for topic in child_topics:
			self.children.append(CategoryNode(self.level + 1, self, topic.lower()))
		return len(child_topics)

	# if child nodes have not been made, creates then and returns how many have been created
	def make_children(self, model, prompt_gen):
		if (self.has_children()):
			return 0
		child_topics = None
		if (model._generation_config["response_mime_type"] == 'application/json'):
			child_topics = get_and_parse_ast(model, prompt_gen.generate_prompt(category = self.topic))
		else:
			child_topics = get_and_parse_topics(model, prompt_gen.generate_prompt(category = self.topic))
		
		return self.add_children(child_topics)

	def save(self, file_path):
		with open(file_path, "w+") as f:
			for child in self.children:
				f.write(child.topic + "\n")

	def __repr__(self):
		out = str(self.level) + "|" + self.topic + " ["
		child_str = [str(c) for c in self.children]
		out += ", ".join(child_str)
		out += "]"
		return out

class CategoryGenerator(object):
	def __init__(self, model):
		self.start = 'general'
		self.level = -1
		self.topics = []
		self.topic_prompt = TopicGenerator()
		self.model = model

		# populate the first layer
		self.topics.append(get_and_parse_topics(self.model, self.topic_prompt.generate_prompt(category = self.start)))

	def get_random_topic(level : int):
		level_at = 0
		rand_choices = [random.randint(0, len(self.topics[0]))]
		while (level_at < level):
			return

	def __repr__(self):
		out = ''
		for i in range(self.level + 1):
			out += "level " + str(i) + ": " + ", ".join(self.topics[i]) + "\n"
		return out