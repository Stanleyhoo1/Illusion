import os
import json
from dotenv import load_dotenv
from strands import Agent, tool
from strands.models.gemini import GeminiModel
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse # Added for URL parsing in resolve_homepage

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
# Tools
# -------------------------------

@tool
def resolve_homepage(company: str) -> str:
    """
    Resolve the most likely homepage, prioritizing the exact root domain 
    (e.g., microsoft.com) with an empty path, and strictly filtering subdomains.
    """
    # Defensive import for Valyu
    try:
        from valyu import Valyu
    except ImportError:
        return f"https://{company.lower().replace(' ', '')}.com"

    if not VALYU_API_KEY:
        return f"https://{company.lower().replace(' ', '')}.com"

    company_slug = company.lower().replace(' ', '')
    valyu = Valyu(api_key=VALYU_API_KEY)
    query = f"{company} official website"

    try:
        resp = valyu.search(query=query, search_type="web", max_num_results=5)
        results = getattr(resp, "results", [])
    except Exception:
        return f"https://{company_slug}.com"

    urls = [getattr(result, "url", "") for result in results if getattr(result, "url", "")]

    if not urls:
        return f"https://{company_slug}.com"

    # 1. Determine the expected root domain (e.g., "microsoft.com")
    if company_slug == "google":
        target_domain = "google.com"
    elif company_slug == "microsoft":
        target_domain = "microsoft.com"
    else:
        target_domain = f"{company_slug}.com"
    
    # Hosts that are considered the primary homepage
    primary_hosts = [target_domain, f"www.{target_domain}"]
    
    filtered_urls = []
    
    # Define additional domains to strictly exclude
    strict_exclude_domains = [
        "wikipedia.org", "facebook.com", "linkedin.com", "youtube.com", 
        "iis.net", "office.com", "azure.com", "cloud.microsoft", "news.microsoft.com"
    ]

    for url in urls:
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc.lower()
        path = parsed_url.path.strip('/')

        # --- Strict Exclusion First ---
        if any(domain in hostname for domain in strict_exclude_domains):
            continue

        # PRIMARY CHECK: Target Hostname & Empty Path
        if hostname in primary_hosts:
            # If the path is empty or just a simple language code (e.g., 'en-us'), 
            # consider it the homepage and return immediately.
            if not path or path.count('/') == 0:
                return url
            
            # If it's the primary domain but has a path, treat it as a high-priority fallback.
            filtered_urls.insert(0, url)
            continue
            
        # --- General Filtering for Other Links ---
        
        # Check for deep paths (general heuristic for non-homepage URLs)
        if path.count('/') > 1:
            continue
            
        filtered_urls.append(url)

    # 3. Prefer regional TLDs from the filtered list (This is the least preferred option)
    preferred_tlds = [".co.uk", ".de", ".fr", ".nl", ".ca", ".org", ".io", ".net", ".com"]
    
    for tld in preferred_tlds:
        for url in filtered_urls:
            if tld in url:
                return url

    # 4. Fallback to the top filtered result, or generic guess
    return filtered_urls[0] if filtered_urls else f"https://{company_slug}.com"


@tool
def fetch_url(url: str) -> list | dict:
    """
    Fetch a URL using Playwright and return cookies, localStorage, and sessionStorage.
    Handles consent banners and dynamic JS cookies.
    Returns a list of items on success, or a dict {'error': 'message'} on failure.
    """
    items = []
    error_message = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/117.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()
            
            # Use 'domcontentloaded' and increase timeout for better reliability
            page.goto(url, wait_until="domcontentloaded", timeout=30000) 

            # Attempt to interact with consent banners (more robust heuristic)
            try:
                accept_button_selector = (
                    'button:has-text("Accept"), button:has-text("Agree"), '
                    'a:has-text("Accept"), a:has-text("Agree"), '
                    '[aria-label*="accept"]:visible, [id*="accept"]:visible, '
                    '[class*="accept"]:visible'
                )
                
                page.wait_for_selector(accept_button_selector, timeout=5000)
                page.click(accept_button_selector, timeout=1000)
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                pass
            except Exception:
                pass

            # Scroll page to trigger JS cookies (with document.body check)
            page.evaluate("if (document.body) { window.scrollTo(0, document.body.scrollHeight); }")
            page.wait_for_timeout(2000)

            # Collect cookies
            cookies = context.cookies()
            for c in cookies:
                items.append({
                    "cookieID": c.get("name"),
                    "content_summary": f"HTTP Cookie from domain {c.get('domain')}. Expires: {c.get('expires')}, secure: {c.get('secure')}.",
                    "relevance": 1.0
                })

            # DEFENSIVE LOCAL STORAGE COLLECTION
            local_storage = page.evaluate("""() => {
                try {
                    return Object.assign({}, window.localStorage);
                } catch (e) {
                    return {};
                }
            }""")
            for k, v in local_storage.items():
                items.append({
                    "cookieID": k,
                    "content_summary": "Item stored in localStorage, used for persistent client-side data storage.",
                    "relevance": 0.8
                })

            # DEFENSIVE SESSION STORAGE COLLECTION
            session_storage = page.evaluate("""() => {
                try {
                    return Object.assign({}, window.sessionStorage);
                } catch (e) {
                    return {};
                }
            }""")
            for k, v in session_storage.items():
                items.append({
                    "cookieID": k,
                    "content_summary": "Item stored in sessionStorage, used for temporary data storage during the user's session.",
                    "relevance": 0.8
                })

            browser.close()

    except PlaywrightTimeoutError as e:
        error_message = f"Playwright Timeout: Failed to navigate to {url} within 30 seconds or elements took too long to load. {e}"
    except Exception as e:
        error_message = f"Failed to fetch URL and extract cookie data: A general error occurred during fetching {url}: {str(e)}"

    if error_message:
        return {"error": error_message}
    
    return items

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