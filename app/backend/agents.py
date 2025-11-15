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
You are the MASTER CONTROLLER AGENT.

Your job is to orchestrate multiple specialized agents to complete a transparency audit.

You must:
- ALWAYS return valid pure JSON.
- NEVER include explanation, markdown, or commentary.
- ONLY output JSON objects.
- Use the schema:

{
  "action": "complete" | "call_agent" | "error",
  "next_agent": "<agent-name-or-null>",
  "payload": { }
}

Meaning:
- "call_agent" → master wants a sub-agent tool to run.
- "complete" → master is done and returning final structured results.
- "error" → master encountered an issue; payload must contain details.
"""

def master_agent():
    agent = Agent(
        model=model,
        tools = [],
        system_prompt=MASTER_SYSTEM_PROMPT,
        response_format="json"
    )
    return agent
