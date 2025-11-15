# Search for policies and links
import os

from strands import Agent
from strands.models.gemini import GeminiModel

from .tools import valyu_search, SearchResults


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

search_agent = Agent(
    model=model, tools=[valyu_search], structured_output_model=SearchResults
)

if __name__ == "__main__":
    response = search_agent(input("Search with Valyu: "))
    output: SearchResults = response.structured_output
    print(output.results)
