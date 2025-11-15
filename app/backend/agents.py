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
from search_agent import search_agent

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

You have access to a tool called `search_agent` that finds
privacy / data-usage related URLs for a company or website.

When given a task, you MUST:
1. Call `search_agent` with an appropriate query string.
2. Wait for the tool result.
3. Then reply with FINAL JSON in this schema:

{
  "status": "success" | "error",
  "query": "<original user query>",
  "sources": [...],          // copied / adapted from search_agent output
  "notes": "<optional notes or null>"
}

Output ONLY JSON, no markdown, no explanations.
"""



def master_agent(query: str):
    agent = Agent(
        tools=[search_agent],
        model=model,
        system_prompt=MASTER_SYSTEM_PROMPT,
    )
    result = agent(query)
    text = getattr(result, "text", str(result)).strip()
    # Remove Markdown JSON fencing if the model adds it
    if text.startswith("```json"):
        text = text[7:]  # remove ```json
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    data = json.loads(text)
    return data

query = "Find Anthropic data collection and usage practices and return structured findings and sources where we can find their policies."

res = master_agent(query)
