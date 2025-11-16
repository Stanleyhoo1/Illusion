import os
import json
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.gemini import GeminiModel

from .tools.fetch_url_tool import fetch_url
from .tools.resolve_homepage_tool import resolve_homepage

# -------------------------------
# Environment
# -------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
VALYU_API_KEY = os.getenv("VALYU_API_KEY")

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
# Wrapper Tool
# -------------------------------
@tool
def cookie_agent(companyName: str) -> str:
    """
    Main tool to find a company's homepage, fetch its client-side storage data (cookies, 
    localStorage, sessionStorage), and summarize the results using the Cookie-Extraction Agent.
    """
    raw_output = cookie_subagent(companyName)

    # Standardize raw_output to a string for parsing
    if isinstance(raw_output, dict):
        raw_output = json.dumps(raw_output)
    elif not isinstance(raw_output, str):
        raw_output = str(raw_output)

    json_text = extract_first_json(raw_output)
    
    # 1. Handle case where the model returns no JSON
    if json_text is None:
        if "error" in raw_output.lower():
            # Attempt to extract the error message from the raw tool output
            try:
                error_msg = json.loads(raw_output).get("error", "Unknown tool error.")
            except:
                error_msg = "Unknown tool error (raw output not JSON)."
            return json.dumps({
                "status": "error",
                "results": [],
                "error_message": f"Tool execution failed: {error_msg}"
            }, indent=2)
        
        return json.dumps({
            "status": "error",
            "results": [],
            "error_message": "No JSON object found in model output. Model failed to adhere to the strict output format."
        }, indent=2)

    # 2. Handle case where the returned JSON is invalid
    try:
        parsed = json.loads(json_text)
    except Exception as e:
        return json.dumps({
            "status": "error",
            "results": [],
            "error_message": f"Invalid JSON returned by model: {str(e)}. Raw output fragment: {json_text[:200]}"
        }, indent=2)

    # 3. Handle case where the JSON is valid but results are empty
    if not parsed.get("results") and parsed.get("status") == "success":
        parsed["status"] = "error"
        parsed["error_message"] = parsed.get("error_message") or "No cookies, localStorage, or sessionStorage could be extracted after page load."
        
    return json.dumps(parsed, indent=2)