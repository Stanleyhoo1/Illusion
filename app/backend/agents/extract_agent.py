import os
import json
from typing import Any, Dict, List

from dotenv import load_dotenv
from strands import Agent
from strands.models.gemini import GeminiModel


# Adjust this import to your actual fetch tool
from agents.tools.fetch_tool import fetch_url

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EXTRACT_AGENT_SYSTEM = """
You are the EXTRACT AGENT.

Your goal:
Given an array of policy URLs and a task prompt (e.g., "extract only data collection practices"),
you MUST visit each URL, read its content using the fetch tool, and extract ONLY the relevant information.

Rules:
1. Use the `fetch_url` tool to retrieve clean webpage text.
2. Extract ONLY information relevant to the task_prompt.
   Examples:
     - If task_prompt = "data collection", extract only:
         - categories of data collected
         - when/why data is collected
     - If task_prompt = "data sharing", extract:
         - who data is shared with
         - purpose of sharing
         - whether data is sold
3. Ignore unrelated sections (billing terms, shipping, product info, etc.).
4. For each URL, return a JSON object containing:
   - url
   - content_summary: short, focused summary (2–5 sentences)
   - extracted_points: list of short bullet points containing ONLY relevant facts
   - relevance: float between 0 and 1 (confidence in relevance)

STRICT OUTPUT FORMAT:

{
  "status": "success" | "error",
  "task_prompt": "<string>",
  "results": [
    {
      "url": "<string>",
      "content_summary": "<string>",
      "extracted_points": ["...", "..."],
      "relevance": <float between 0 and 1>
    }
  ],
  "error_message": "<string or null>"
}

NO MARKDOWN. NO COMMENTARY. NO CODE FENCES.
"""

extract_subagent_model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

extract_subagent = Agent(
    model=extract_subagent_model,
    system_prompt=EXTRACT_AGENT_SYSTEM,
    tools=[fetch_url],
)


@tool
def extract_agent(sources: List[Dict[str, Any]], task_prompt: str) -> Dict[str, Any]:
    """
    Tool wrapper around the extract subagent.

    Inputs:
      - sources: list of { url, policy_type, ... } from search_agent
      - task_prompt: string describing what to extract

    Output: structured extraction JSON
    """

    message = json.dumps({"sources": sources, "task_prompt": task_prompt})

    result = extract_subagent(message)

    # Strands may return dict or ModelResponse-like object
    if isinstance(result, dict):
        return result

    text = getattr(result, "text", str(result)).strip()

    # Strip accidental fences
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
        data = {
            "status": "error",
            "task_prompt": task_prompt,
            "results": [],
            "error_message": f"Could not parse JSON from extract_subagent: {text[:200]}",
        }

    return data
