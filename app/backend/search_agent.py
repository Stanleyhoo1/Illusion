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
import tldextract

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SEARCH_AGENT_SYSTEM = """
You are the SEARCH AGENT.

Your job is to discover official policy URLs for a given company or website.

Return ONLY VALID JSON, no text or markdown.

Steps:
1. If the input is a COMPANY NAME, perform a web search to find the official homepage.
2. If the input is a URL, normalize it to the base domain.
3. Search for these pages:
   - Privacy Policy
   - Terms of Service
   - Cookie Policy
   - Data Usage / Data Protection
4. Use web search or fallback heuristics to detect likely URL paths.
5. Output all discovered URLs in clean JSON.

Return format:
{
  "status": "success" | "error",
  "domain": "<canonical domain>",
  "policies": [
    {"type": "privacy_policy", "url": "..."},
    {"type": "terms_of_service", "url": "..."},
    {"type": "cookie_policy", "url": "..."},
    {"type": "data_usage", "url": "..."}
  ]
}
"""

@tool
def search_agent(query: str):
    """
    Input: company name or URL
    Output: JSON with identified policy URLs
    """

    # Create agent instance
    model = GeminiModel(
        client_args={"api_key": GEMINI_API_KEY},
        model_id="gemini-2.5-flash",
        params={"temperature": 0.1},
    )

    agent = Agent(
        tools=[],
        model=model,
        system_prompt=SEARCH_AGENT_SYSTEM,
    )

    # ---------------------------
    # Normalize domain
    # ---------------------------
    def extract_domain(q):
        if q.startswith("http://") or q.startswith("https://"):
            ext = tldextract.extract(q)
            return f"{ext.domain}.{ext.suffix}"
        # treat it as company name → later resolved via search
        return None

    domain = extract_domain(query)

    results = {
        "status": "success",
        "domain": None,
        "policies": []
    }

    # ---------------------------
    # 1. Try to resolve company → domain via Exa search
    # ---------------------------
    homepage = None
    if domain is None:
        try:
            search = agent.tool.exa_search(
                query=f"{query} official website",
                text=True
            )
            # choose the top result
            if search and "results" in search and len(search["results"]) > 0:
                homepage = search["results"][0]["url"]
                ext = tldextract.extract(homepage)
                domain = f"{ext.domain}.{ext.suffix}"
        except Exception:
            pass

    results["domain"] = domain

    # Fallback if domain still not resolved
    if domain is None:
        return {
            "status": "error",
            "message": "Domain could not be resolved from query."
        }

    base_url = f"https://{domain}"

    # ---------------------------
    # 2. Build likely policy URLs
    # ---------------------------
    candidate_paths = [
        ("privacy_policy", ["privacy", "privacy-policy", "legal/privacy"]),
        ("terms_of_service", ["terms", "terms-of-service", "legal/terms"]),
        ("cookie_policy", ["cookie-policy", "cookies"]),
        ("data_usage", ["data", "data-protection", "data-usage"])
    ]

    # ---------------------------
    # 3. Try Exa search to confirm real URLs
    # ---------------------------
    discovered = {}

    try:
        indexed = agent.tool.exa_search(
            query=f"{domain} privacy policy terms cookies",
            text=True
        )
        if indexed and "results" in indexed:
            for r in indexed["results"]:
                url = r.get("url", "")
                url_lower = url.lower()

                if "privacy" in url_lower:
                    discovered["privacy_policy"] = url
                if "terms" in url_lower:
                    discovered["terms_of_service"] = url
                if "cookie" in url_lower:
                    discovered["cookie_policy"] = url
                if "data" in url_lower:
                    discovered["data_usage"] = url
    except Exception:
        pass

    # ---------------------------
    # 4. Add fallback heuristic URLs
    # ---------------------------
    for policy_type, paths in candidate_paths:
        if policy_type not in discovered:
            for p in paths:
                candidate_url = f"{base_url}/{p}"
                discovered[policy_type] = candidate_url
                break

    # ---------------------------
    # 5. Assemble JSON output
    # ---------------------------
    for ptype, url in discovered.items():
        results["policies"].append({
            "type": ptype,
            "url": url
        })

    return results
