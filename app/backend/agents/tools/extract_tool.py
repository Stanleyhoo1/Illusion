import os

from strands import tool

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
HOLISTIC_AI_TEAM_ID = os.getenv("TEAM_ID")
HOLISTIC_AI_API_TOKEN = os.getenv("API_TOKEN")


@tool
def extract_context(sourceDictStr: str) -> str:
    """Extracts important information from a policy source described by a JSON string
    and returns a structured JSON output.
    """

    import re
    import json
    import os
    from urllib.parse import urlparse
    import requests
    from bs4 import BeautifulSoup
    from pypdf import PdfReader
    from strands import get_chat_model

    # -------------- Helper: classify the input ----------------
    def classify_input(s: str) -> str:
        s = s.strip()

        parsed = urlparse(s)
        if parsed.scheme in ("http", "https") and parsed.netloc:
            return "url"

        domain_pattern = re.compile(
            r"^(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+(?:/.*)?$"
        )
        windows_drive_pattern = re.compile(r"^[a-zA-Z]:\\")
        if domain_pattern.match(s) and not windows_drive_pattern.match(s):
            return "url"

        if s.lower().endswith(".pdf"):
            if os.path.isabs(s) or "/" in s or "\\" in s:
                return "pdf_path"

        return "unknown"

    # -------------- Parse JSON ----------------
    try:
        sourceDict = json.loads(sourceDictStr)
    except json.JSONDecodeError:
        return "Invalid JSON string."

    if "src" not in sourceDict or "document_name" not in sourceDict:
        return "JSON must contain 'src' and 'document_name'."

    src = sourceDict["src"]
    document_name = sourceDict["document_name"]

    sourceType = classify_input(src)
    if sourceType == "unknown":
        return "unknown source type"

    # -------------- Extract raw content ----------------
    raw_text = ""

    # PDF
    if sourceType == "pdf_path":
        try:
            reader = PdfReader(src)
            for page in reader.pages:
                raw_text += page.extract_text() or ""
        except Exception as e:
            return json.dumps({"error": f"Failed to read PDF: {e}"})

    # URL
    elif sourceType == "url":
        try:
            if not src.startswith("http"):
                src = "https://" + src

            response = requests.get(src, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            raw_text = soup.get_text("\n")
            raw_text = "\n".join(
                line.strip() for line in raw_text.splitlines() if line.strip()
            )

        except Exception as e:
            return json.dumps({"error": f"Failed to fetch URL: {e}"})

    # -------------- LLM Processing ----------------
    llm = get_chat_model("claude-3-5-sonnet")

    prompt = f"""
You are an expert policy analyst.

Extract and summarize the content from the provided document into a STRICT JSON object.

Document Name: {document_name}
Source Type: {sourceType}

Raw Extracted Content:
----------------------
{raw_text}

Respond ONLY with valid JSON. No explanations, no markdown.

Your JSON MUST follow this structure exactly:

{{
  "overview": "string",
  "purpose": "string",
  "key_requirements": ["string", "string", "..."],
  "roles_and_responsibilities": ["string", "string", "..."],
  "processes_and_procedures": ["string", "string", "..."],
  "risks_compliance_enforcement": ["string", "string", "..."],
  "other_important_details": ["string", "string", "..."]
}}
"""

    response = llm.invoke(prompt)

    # Validate that response is valid JSON (LLMs can slip)
    try:
        parsed = json.loads(response.content)
        return json.dumps(parsed, indent=2)
    except Exception:
        # fallback: wrap content as text
        return json.dumps(
            {
                "error": "Model did not return valid JSON.",
                "raw_model_output": response.content,
            },
            indent=2,
        )
