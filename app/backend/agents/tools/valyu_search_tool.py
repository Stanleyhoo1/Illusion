import os

from datetime import datetime

from dotenv import load_dotenv
from strands import tool

from pydantic import BaseModel, Field
from valyu import SearchResponse, Valyu


load_dotenv()

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
valyu = Valyu(api_key=VALYU_API_KEY)


class NameAndLink(BaseModel):
    """Model that contains the document type (name) and the document URL."""

    document_name: str = Field(description="Name of the document")
    src: str = Field(description="Source of the document")
    summary: str = Field(description="Summary of the document")
    relevance: str = Field(description="Why the document is relevant")
    timestamps: datetime = Field(description="Retrieval date")


class SearchResults(BaseModel):
    """Model that contains a list of results."""

    results: list[NameAndLink] = Field(
        description="The list of results"  # , where the first field is the document name ('document_name'), and the second field is the source (url or path) of the document ('src')"
    )


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
        max_num_results=20,  # Limit to top 5 results
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
        model=model, tools=[valyu_search], structured_output_model=SearchResults
    )

    pprint(agent("Google Policies").structured_output)
