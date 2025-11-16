import os
import json
from typing import Any, Dict, List
import ast

from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.gemini import GeminiModel


# Adjust this import to your actual fetch tool
# from agents.tools.fetch_tool import fetch_url
from .tools import extract_context, cookie_tool

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EXTRACT_AGENT_SYSTEM = """
You are the EXTRACT AGENT.

Your goal:
Given an array of policy URLs and a task prompt (e.g., "extract only data collection practices"),
you MUST visit each URL, read its content using the fetch tool, and extract ONLY the relevant information.

Rules:
1. Use the `extract_context` tool to retrieve clean webpage text.
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
   - content_summary: short, focused summary (2-5 sentences)
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

CRITICAL JSON RULES:
- Use ONLY double quotes (") for JSON keys and string values.
- You MAY include single quotes (') inside strings, but do NOT escape them with a backslash.
- NEVER output the sequence \\' anywhere in the JSON.
- All backslashes MUST be part of valid JSON escapes: \\\", \\\\, \\/, \\b, \\f, \\n, \\r, \\t, or \\uXXXX.
- The final assistant message MUST be exactly one valid JSON object, with no extra text.
"""

extract_subagent_model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

extract_subagent = Agent(
    model=extract_subagent_model,
    system_prompt=EXTRACT_AGENT_SYSTEM,
    tools=[extract_context, cookie_tool],
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

    from langsmith.run_helpers import trace
    import uuid

    run_id = str(uuid.uuid4())

    # Create root trace
    with trace(
        name="extract-agent-root",
        run_id=run_id,
        metadata={"task_prompt": task_prompt, "num_sources": len(sources)},
        tags=["extract-agent", "observability"],
        project=os.getenv("LANGSMITH_PROJECT", "strands-extract-agent")
    ):

        # --------------------------
        # BEGIN ORIGINAL FUNCTION
        # --------------------------

        message = json.dumps({"sources": sources, "task_prompt": task_prompt})

        result = extract_subagent(message)

        # Strands may return dict or ModelResponse-like object
        if isinstance(result, dict):
            return result

        text = getattr(result, "text", str(result)).strip()

        # Strip accidental fences
        if text.startswith("```json"):
            text = text[7:].strip()
        if text.startswith("```"):
            text = text[3:].strip()
        if text.endswith("```"):
            text = text[:-3].strip()

        # Isolate JSON
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1:
            json_str = text[first:last + 1]
        else:
            json_str = text

        # Fix invalid escape sequences
        json_str = json_str.replace("\\'", "'")

        # Parse JSON or fallback
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            try:
                lit = ast.literal_eval(json_str)
                if isinstance(lit, dict):
                    return lit
            except Exception:
                pass

            return {
                "status": "error",
                "task_prompt": task_prompt,
                "results": [],
                "error_message": f"Could not parse JSON from extract_subagent: {json_str[:200]}",
            }
