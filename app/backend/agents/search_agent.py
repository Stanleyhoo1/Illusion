import os
import json
from typing import Any

from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.gemini import GeminiModel

from agents.tools.valyu_search_tool import valyu_search

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

You MUST ALWAYS return ONLY valid JSON, with this exact schema:

{
  "status": "success" | "error",
  "company_or_url": "<original input>",
  "resolved_domain": "<domain-or-null>",
  "sources": [
    {
      "url": "<string>",
      "policy_type": "privacy_policy" | "terms_of_service"
                     | "cookie_policy" | "data_protection" | "other",
      "title": "<string or null>",
      "summary": "<string or null>",
      "relevance": <float between 0 and 1>
    }
  ],
  "error_message": "<string or null>"
}

Rules:
- No markdown, no commentary, no code fences.
- If something fails, set "status": "error" and explain in "error_message".
- Sort sources by relevance descending.
"""

search_subagent_model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

search_subagent = Agent(
    model=search_subagent_model,
    system_prompt=SEARCH_AGENT_SYSTEM,
    tools=[valyu_search],
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
    """
    # Run the subagent with the raw company_or_url as the user message.
    result = search_subagent(company_or_url)

    text = getattr(result, "text", str(result)).strip()

    # Be robust to occasional ```json fences, just in case.
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
        # Fallback error object if the model misbehaves

        data = {
            "status": "error",
            "company_or_url": company_or_url,
            "resolved_domain": None,
            "sources": [],
            "error_message": f"Could not parse JSON from search_subagent: {text[:200]}",
        }

    return data
