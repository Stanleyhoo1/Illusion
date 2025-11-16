from strands import tool
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

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