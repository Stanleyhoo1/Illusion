import os
import json
import threading
from typing import Optional

from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.gemini import GeminiModel
from string import Template

from playwright.sync_api import (
    sync_playwright, Page, Browser, BrowserContext,
    TimeoutError as PWTimeout
)

import re
from agents.search_agent import search_agent
from agents.extract_agent import extract_agent

from pprint import pprint

# -------------------------------------------------------------------
# Env / LLM
# -------------------------------------------------------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

model = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.1},
)

MASTER_SYSTEM_PROMPT = """
You are the MASTER AGENT.

You have access to two tools:

1) search_agent(company_or_url: str) -> JSON
   - Finds privacy / data-usage related URLs and returns a JSON object:
     {
       "status": "success" | "error",
       "company_or_url": "...",
       "resolved_domain": "... or null",
       "sources": [ { "url": "...", "policy_type": "...", ... } ],
       "error_message": "..."
     }

2) extract_agent(sources: list, task_prompt: str) -> JSON
   - Takes the 'sources' array from search_agent and a task_prompt
     (e.g. "data collection and usage practices") and returns:
     {
       "status": "success" | "error",
       "task_prompt": "...",
       "results": [
         {
           "url": "...",
           "content_summary": "...",
           "extracted_points": ["...", "..."],
           "relevance": 0.0-1.0
         }
       ],
       "error_message": "..."
     }

Your job, given a natural language user query, is to:

1. Interpret the query and identify the target company / website.
2. Call search_agent with an appropriate short query string
   (usually the company name or official domain).
3. Inspect the JSON returned by search_agent.
   - If search_agent.status != "success" OR sources is empty,
     you MUST return a FINAL JSON object with status "error".
4. If search_agent succeeds, call extract_agent with:
   - sources: the "sources" array from search_agent
   - task_prompt: a short phrase summarising what to extract
     (derived from the user query, e.g. "data collection and usage practices").
5. After extract_agent returns, produce ONE FINAL JSON object with this schema:

{
  "status": "success" | "error",
  "query": "<original user query>",
  "search_result": { ...search_agent JSON... } | null,
  "extraction_result": { ...extract_agent JSON... } | null,
  "notes": "<optional notes for the caller or null>"
}

Rules:
- You MUST call search_agent at least once for each user query.
- If search_agent succeeds and returns sources, you MUST call extract_agent exactly once.
- Output ONLY a single JSON object as described above.
- NO markdown, NO explanations, NO code fences.
"""


def master_agent(query: str):
    agent = Agent(
        tools=[search_agent, extract_agent],
        model=model,
        system_prompt=MASTER_SYSTEM_PROMPT,
    )
    result = agent(query)

    text = getattr(result, "text", str(result)).strip()

    # Remove Markdown JSON fencing if the model adds it
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    data = json.loads(text)
    return data


query = (
    "Find Anthropic data collection and usage practices and return structured "
    "findings and sources where we can find their policies."
)

res = master_agent(query)
pprint(res)
