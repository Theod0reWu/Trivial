import json
import textwrap
import os

import google.generativeai as genai
import google.ai.generativelanguage as glm

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

import numpy as np

from IPython.display import Markdown

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def wikipedia_search(search_queries: list[str]) -> list[str]:
  """Search wikipedia for each query and summarize relevant docs."""
  n_topics=3
  search_history = set() # tracking search history
  search_urls = []
  mining_model = genai.GenerativeModel('gemini-pro')
  summary_results = []

  for query in search_queries:
    print(f'Searching for "{query}"')
    search_terms = wikipedia.search(query)

    print(f"Related search terms: {search_terms[:n_topics]}")
    for search_term in search_terms[:n_topics]: # select first `n_topics` candidates
      if search_term in search_history: # check if the topic is already covered
        continue

      print(f'Fetching page: "{search_term}"')
      search_history.add(search_term) # add to search history

      try:
        # extract the relevant data by using `gemini-pro` model
        page = wikipedia.page(search_term, auto_suggest=False)
        url = page.url
        print(f"Information Source: {url}")
        search_urls.append(url)
        page = page.content
        response = mining_model.generate_content(textwrap.dedent(f"""\
            Extract relevant information
            about user's query: {query}
            From this source:

            {page}

            Note: Do not summarize. Only Extract and return the relevant information
        """))

        urls = [url]
        if response.candidates[0].citation_metadata:
          extra_citations = response.candidates[0].citation_metadata.citation_sources
          extra_urls = [source.url for source in extra_citations]
          urls.extend(extra_urls)
          search_urls.extend(extra_urls)
          print("Additional citations:", response.candidates[0].citation_metadata.citation_sources)
        try:
          text = response.text
        except ValueError:
          pass
        else:
          summary_results.append(text + "\n\nBased on:\n  " + ',\n  '.join(urls))

      except DisambiguationError:
        print(f"""Results when searching for "{search_term}" (originally for "{query}")
        were ambiguous, hence skipping""")

      except PageError:
        print(f'{search_term} did not match with any page id, hence skipping.')

  print(f"Information Sources:")
  for url in search_urls:
    print('    ', url)

  return summary_results

# example = wikipedia_search(["What are LLMs?"])

search = wikipedia.search("shakespeare", results = 20)
print(search)
for result in search:
  if ("(disambiguation)" not in result):
    try:
      print(wikipedia.page(result, auto_suggest = False))
    except wikipedia.exceptions.DisambiguationError as e:
      print (e.options)