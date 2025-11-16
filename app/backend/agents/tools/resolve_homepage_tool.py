import os
from strands import tool
from urllib.parse import urlparse

VALYU_API_KEY = os.getenv("VALYU_API_KEY")

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