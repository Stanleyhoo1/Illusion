# Search for policies and links
import os

from strands import Agent
from strands.models.gemini import GeminiModel

from .tools import valyu_search


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
Only use legal documentation from official sources (the companies' websites).
"""

model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

search_agent = Agent(
    model=model,
    tools=[valyu_search],
    system_prompt=SYSTEM_PROMPT,
)

if __name__ == "__main__":
    from pprint import pprint

    response = search_agent(input("Search with Valyu: "))
    pprint(response)
