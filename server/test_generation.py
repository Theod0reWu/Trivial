import google.generativeai as genai
import numpy as np
import os
import asyncio
import wikipedia

from game_generation.category_generator import CategoryTree

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

config = genai.types.GenerationConfig(
    candidate_count = 1,
    response_mime_type = "application/json",
)

# model = genai.GenerativeModel('gemini-1.5-pro', generation_config = config)
model = genai.GenerativeModel('gemini-1.5-flash', generation_config = config)
# prompt = TopicGenerator('./prompts/topics_json.txt').generate_prompt(category = "history")
# output = get_and_parse_ast(model, prompt)
# print(output)

cat_tree = CategoryTree()

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# print(asyncio.run(cat_tree.get_random_topic_async(model, 3)))
# print(asyncio.run(cat_tree.get_random_topic_async(model, 3)))

counts = {}

num_topics = 1
for i in range(num_topics):
    topic = cat_tree.get_random_topic(model, 2)
    if (topic in counts):
        counts[topic] += 1
    else:
        counts[topic] = 1
    # print(cat_tree.get_n_random_topics(model, 2, 3))

# print(counts)
x = [(counts[i], i) for i in counts]
print(sorted(x))

cat_tree.save_checkpoint()
print(cat_tree)