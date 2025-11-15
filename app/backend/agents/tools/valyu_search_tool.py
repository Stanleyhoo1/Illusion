import os

from dotenv import load_dotenv
from strands import tool

from valyu import SearchResponse, Valyu


load_dotenv()

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
valyu = Valyu(api_key=VALYU_API_KEY)


@tool
def valyu_search(prompt: str) -> SearchResponse | None:
    """Returns Valyu results from a prompt

    Args:
        prompt (str): the prompt to search for

    Returns:
        SearchResponse: the response with all the results
    """
    response = valyu.search(
        prompt,
        max_num_results=5,  # Limit to top 5 results
        # max_price=10,  # Maximum price per thousand queries (CPM)
        # fast_mode=False,  # Enable fast mode for quicker, shorter results
    )

    return response


if __name__ == "__main__":
    from pprint import pprint
    from strands import Agent
    from strands.models.gemini import GeminiModel

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    model = GeminiModel(
        client_args={"api_key": GEMINI_API_KEY},
        model_id="gemini-2.5-flash",
        params={"temperature": 0.1},
    )
    agent = Agent(
        model=model,
        tools=[valyu_search],
    )

    pprint(agent("Google Policies"))
