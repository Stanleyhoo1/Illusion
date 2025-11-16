import os
from typing import Any, Literal


from dotenv import load_dotenv
from pydantic import BaseModel, Field
from strands import Agent, tool
from strands.models.gemini import GeminiModel
from strands.types.exceptions import StructuredOutputException

from .tools.valyu_search_tool import valyu_search

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SEARCH_AGENT_SYSTEM = """
You are the SEARCH AGENT.

Input: a company name (e.g. "Anthropic") OR a URL
(e.g. "https://www.anthropic.com/").

You have access to a web search tool called `valyu_search`.
Use it to find pages related to the company's data and privacy practices.

Your goals:
1. Resolve what company / site is being referred to.
2. Use `valyu_search_tool` with smart queries to find:
   - Privacy policy
   - Terms of service / terms of use
   - Cookie policy
   - Data protection / data usage pages
   - Any other clearly relevant pages about data collection / usage.
3. For each relevant result, infer:
   - policy_type:
       "privacy_policy" | "terms_of_service" | "cookie_policy"
       | "data_protection" | "other"
   - url
   - title
   - a short summary (2-4 sentences) focused ONLY on:
       - what data is collected,
       - how it is used,
       - how it is shared,
       - retention / storage,
       - user rights or controls.
   - relevance: a float between 0 and 1
4. Prefer official pages on the company's own domain.
5. Avoid duplicates (same URL more than once).
6. If no relevant sources are found, explain why.
7. Try to limit sources to 5-10 high-quality results, if some repeat the same information, pick the best ones to keep.

You MUST ALWAYS return an output that follows the structured output, with this exact schema:

{
  "status": "success" | "error",
  "company_or_url": "<original input>",
  "resolved_domain": "<domain or None>",
  "sources": [
    {
      "url": "<string>",
      "policy_type": "privacy_policy" | "terms_of_service"
                     | "cookie_policy" | "data_protection" | "other",
      "title": "<string or null>",
      "summary": "<string or null>",
      "relevance": <float between 0 and 1>,
      "relevance_explanation": "<brief explanation of relevance score>"
    }
  ],
  "error_message": "<string or None>"
}

Rules:
- No markdown, no commentary, no code fences.
- If something fails, set "status": "error" and explain in "error_message".
- Sort sources by relevance descending.
- ONLY use sources from the official company domain if possible, no third-party sites like Reddit.
"""


class Source(BaseModel):
    """A source of data."""

    url: str = Field(description="URL of the given policy")
    policy_type: (
        Literal["privacy_policy"]
        | Literal["terms_of_service"]
        | Literal["cookie_policy"]
        | Literal["data_protection"]
        | Literal["other"]
    ) = Field(description="The type of the policy")
    title: str | None = Field(description="The title of the policy")
    summary: str | None = Field(description="The summary of the policy")
    relevance: float = Field(
        description="A score on how relevant the result is", ge=0, le=1
    )


class Result(BaseModel):
    """Result for the Search Agent to return."""

    status: Literal["success"] | Literal["error"] = Field(
        description="The status of the result"
    )
    company_or_url: str = Field(description="The original input")
    resolved_domain: str | None = Field(description="The resolved domain")
    sources: list[Source] = Field(description="The list of sources")
    error_message: str | None = Field(
        description="The error message if there is one, otherwise null", default=None
    )


search_subagent_model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

search_subagent = Agent(
    model=search_subagent_model,
    system_prompt=SEARCH_AGENT_SYSTEM,
    tools=[valyu_search],
    structured_output_model=Result,
)


# ---------------------------------------------------------
# Tool wrapper: callable by the MASTER AGENT
# ---------------------------------------------------------


@tool
def search_agent(company_or_url: str) -> dict[str, Any]:
    """
    Tool wrapper around the search subagent.

    Input: company name or URL
    Output: JSON with identified policy-related sources.
    Retries the subagent once if the first attempt fails or returns no sources.
    """
    last_error_text = None

    for attempt in range(2):  # at most two tries
        result = search_subagent(company_or_url)

        if isinstance(result, dict):
            data = result
        else:
            text = getattr(result, "text", str(result)).strip()

            # Strip possible fences
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                last_error_text = text
                data = {
                    "status": "error",
                    "company_or_url": company_or_url,
                    "resolved_domain": None,
                    "sources": [],
                    "error_message": "JSON parse error in search_subagent",
                }

        # If this attempt looks good, return immediately
        if (
            isinstance(data, dict)
            and data.get("status") == "success"
            and data.get("sources")
        ):
            # annotate how many attempts it took (optional)
            data.setdefault("meta", {})
            data["meta"]["attempts"] = attempt + 1
            return data

        # otherwise loop and try again

    # If we reach here, both attempts failed or returned empty sources
    # return the last error-ish thing we have
    if isinstance(data, dict):
        data.setdefault("meta", {})
        data["meta"]["attempts"] = 2
        if not data.get("error_message") and last_error_text:
            data["error_message"] = (
                data.get("error_message")
                or f"search_agent failed twice; last raw text: {last_error_text[:200]}"
            )
        return data

    # extreme fallback
    return {
        "status": "error",
        "company_or_url": company_or_url,
        "resolved_domain": None,
        "sources": [],
        "error_message": "search_agent failed twice with non-dict response",
        "meta": {"attempts": 2},
    }
