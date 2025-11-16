import os
import json
from dotenv import load_dotenv

from langsmith.run_helpers import traceable, get_current_run_tree

from strands import Agent, tool
from strands.models.gemini import GeminiModel

from .tools.fetch_url_tool import fetch_url
from .tools.resolve_homepage_tool import resolve_homepage

# -------------------------------
# Environment
# -------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# -------------------------------
# System Prompt
# -------------------------------
EXTRACT_AGENT_SYSTEM = """
You are the COOKIE-EXTRACTION AGENT.

Task:
Given a company name, determine the most likely homepage URL using the `resolve_homepage` tool.
Then retrieve cookie data using the `fetch_url` tool.
Extract ONLY cookie-related information (cookies, localStorage, sessionStorage).

Rules:
1. Summarize the content of each extracted item (cookieID, key).
2. Ignore unrelated information from the `fetch_url` output.
3. If no items could be extracted, return status="error".

Output format (strict JSON):

{
  "status": "success" | "error",
  "results": [
    {
      "cookieID": "<string>",
      "content_summary": "<1-sentence summary of its purpose/content>"
    }
  ],
  "error_message": "<string or null>"
}

STRICT JSON RULES:
- Output exactly ONE JSON object.
- Do NOT output additional text before or after JSON.
- JSON must be valid and parseable by json.loads().
"""

# -------------------------------
# Model + Agent
# -------------------------------
cookie_subagent_model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1}
)

cookie_subagent = Agent(
    model=cookie_subagent_model,
    system_prompt=EXTRACT_AGENT_SYSTEM,
    tools=[resolve_homepage, fetch_url]
)

# -------------------------------
# JSON Extraction Helper
# -------------------------------
def extract_first_json(text: str) -> str | None:
    """Safely extracts the first complete JSON object from a string."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i+1]
    return None

# -------------------------------
# Cookie Agent Tool (traced)
# -------------------------------
@tool
def cookie_agent(companyName: str) -> str:
    """Core tool: runs the cookie extraction agent."""

    @traceable(name="cookie-agent-run", metadata={"company": companyName})
    def run_cookie_subagent(companyName: str):
        run = get_current_run_tree()
        if run:
            run.events.append({"name": "agent.start", "data": {"company": companyName}})

        result = cookie_subagent(companyName)

        if run:
            run.events.append({"name": "agent.raw_model_output", "data": {"result": result}})

        return result

    # Run the traced subagent
    raw_output = run_cookie_subagent(companyName)

    # Standardize the output
    if isinstance(raw_output, dict):
        raw_output = json.dumps(raw_output)
    elif not isinstance(raw_output, str):
        raw_output = str(raw_output)

    run = get_current_run_tree()
    if run:
        run.events.append({"name": "json.raw_output", "data": {"raw": raw_output}})

    # Extract JSON
    json_text = extract_first_json(raw_output)
    if json_text is None:
        if run:
            run.events.append({"name": "json.error", "data": {"message": "No JSON found"}})
        return json.dumps({
            "status": "error",
            "results": [],
            "error_message": "No JSON object found in model output."
        }, indent=2)

    # Parse JSON
    try:
        parsed = json.loads(json_text)
        if run:
            run.events.append({"name": "json.success", "data": {"parsed": parsed}})
    except Exception as e:
        if run:
            run.events.append({"name": "json.error", "data": {"message": str(e)}})
        return json.dumps({
            "status": "error",
            "results": [],
            "error_message": f"Invalid JSON returned by model: {str(e)}"
        }, indent=2)

    # Validation
    if not parsed.get("results") and parsed.get("status") == "success":
        if run:
            run.events.append({"name": "agent.fix_status", "data": {"message": "Model returned success but no results"}})
        parsed["status"] = "error"
        parsed["error_message"] = parsed.get("error_message") or "No cookie/localStorage/sessionStorage info found."

    final_json = json.dumps(parsed, indent=2)

    if run:
        run.events.append({"name": "agent.final_output", "data": parsed})

    return final_json