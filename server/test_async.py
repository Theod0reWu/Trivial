from gemini import get_and_parse_topics, get_and_parse_ast
from prompt import TopicGenerator
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])



config = genai.types.GenerationConfig(
    candidate_count = 1,
    response_mime_type = "application/json",
)
model = genai.GenerativeModel('gemini-1.5-pro', generation_config = config)


prompt_gen = TopicGenerator( os.path.join(os.path.dirname(__file__), 'prompts/topics_json.txt'))
output = get_and_parse_topics(model, prompt_gen.generate_prompt(category = "history"))

print(output)