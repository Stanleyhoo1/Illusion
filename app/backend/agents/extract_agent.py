# Extract data from the webpage
import os

from dotenv import load_dotenv
from strands import Agent
from strands.models.gemini import GeminiModel


from .tools import extract_context

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

extract_subagent = Agent(
    model=model,
    tools=[extract_context],
)


# ---------------------------------------------------------
# Tool wrapper: callable by the MASTER AGENT
# ---------------------------------------------------------


# @tool
# def search_agent(company_or_url: str) -> dict[str, Any]:
#     """
#     Tool wrapper around the search subagent.

#     Input: company name or URL
#     Output: JSON with identified policy-related sources.
#     """
#     # Run the subagent with the raw company_or_url as the user message.
#     result = search_subagent(company_or_url)

#     # Depending on Strands version, `result` may already be a dict.
#     if isinstance(result, dict):
#         return result

#     text = getattr(result, "text", str(result)).strip()

#     # Be robust to occasional ```json fences, just in case.
#     if text.startswith("```json"):
#         text = text[7:]
#     if text.startswith("```"):
#         text = text[3:]
#     if text.endswith("```"):
#         text = text[:-3]
#     text = text.strip()

#     try:
#         data = json.loads(text)
#     except json.JSONDecodeError:
#         # Fallback error object if the model misbehaves
#         data = {
#             "status": "error",
#             "company_or_url": company_or_url,
#             "resolved_domain": None,
#             "sources": [],
#             "error_message": f"Could not parse JSON from search_subagent: {text[:200]}",
#         }

#     return data

if __name__ == "__main__":
    extract_subagent(
        '{"src": "https://policies.google.com/privacy?hl=en-US", "document_name": "Google Privacy Policy"}'
    )
