# Generate a summary of the extracted data

import os
import json
from typing import Any, Dict

from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.gemini import GeminiModel

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SUMMARY_AGENT_SYSTEM = """
You are the SUMMARY AGENT.

You take:
- search_result: the raw results from search_agent (contains URLs & policy types)
- extraction_result: the structured extracted points from extract_agent
- user_query: what the user is asking for (e.g., "data collection practices")

Your job is to generate a FINAL TRANSPARENT SUMMARY with the following goals:

1. Summarize the company's data practices clearly and concisely.
2. Provide a multi-dimensional rating system:
   - data_collection_risk: 1–5
   - data_sharing_risk: 1–5
   - tracking_risk: 1–5
   - transparency_score: 1–5
3. Explain WHY you assigned each rating.
   - Refer EXPLICITLY to specific extracted_points and their source URLs.
4. Provide user safety guidance:
   - How users can protect themselves on this platform.
   - What settings they can change.
   - What rights they have (e.g. delete data, opt-out of tracking).
5. Provide a final consumer-friendly summary:
   - “Should users be concerned?”
   - “How careful should users be?”
6. List all sources used, with URLs and relevance.

STRICT OUTPUT FORMAT:
{
  "status": "success" | "error",
  "query": "<original query>",
  "summary": {
    "overview": "<plain-language high-level summary>",
    "key_findings": ["...", "..."],
    "ratings": {
      "data_collection_risk": <1-5>,
      "data_sharing_risk": <1-5>,
      "tracking_risk": <1-5>,
      "transparency_score": <1-5>
    },
    "reasoning": [
      {
        "rating": "<which rating>",
        "evidence": [
          {
            "url": "<source url>",
            "point": "<specific extracted_point from extraction_result>"
          }
        ],
        "explanation": "<why this evidence led to the rating>"
      }
    ],
    "user_protection_advice": ["...", "..."],
    "final_recommendation": "<string>"
  },
  "sources_used": [
    {
      "url": "<string>",
      "policy_type": "<string>",
      "relevance": <float>,
      "title": "<string or null>"
    }
  ],
  "error_message": "<null or string>"
}

RULES:
- No markdown.
- No code fences.
- Citations MUST reference actual URLs from search_result.
- Evidence MUST reference extracted_points from extraction_result.
- If extraction_result.status != success → return status:error.
"""


summary_subagent_model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

summary_subagent = Agent(
    model=summary_subagent_model,
    system_prompt=SUMMARY_AGENT_SYSTEM,
    tools=[],   # no external tools needed here
)
@tool
def summary_agent(
    search_result: Dict[str, Any],
    extraction_result: Dict[str, Any],
    user_query: str
) -> Dict[str, Any]:
    """
    Wrapper tool around the summary subagent, with automatic LangSmith tracing.
    """

    from langsmith.run_helpers import trace
    import uuid

    run_id = str(uuid.uuid4())

    # Root LangSmith run for this invocation
    with trace(
        name="summary-agent-root",
        run_id=run_id,
        metadata={
            "query": user_query,
            "num_search_results": len(search_result.get("results", [])),
            "num_extracted": len(extraction_result.get("results", [])),
        },
        tags=["summary-agent", "observability"],
        project=os.getenv("LANGSMITH_PROJECT", "strands-summary-agent"),
    ):

        # ----------------------------------------------------
        # ORIGINAL LOGIC (unchanged)
        # ----------------------------------------------------

        payload = {
            "search_result": search_result,
            "extraction_result": extraction_result,
            "query": user_query
        }

        message = json.dumps(payload)

        # Run the LLM agent
        result = summary_subagent(message)

        if isinstance(result, dict):
            return result

        text = getattr(result, "text", str(result)).strip()

        # Strip accidental markdown fences
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # Parse JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = {
                "status": "error",
                "query": user_query,
                "summary": None,
                "sources_used": [],
                "error_message": f"Could not parse JSON from summary_subagent: {text[:200]}",
            }

        return data
