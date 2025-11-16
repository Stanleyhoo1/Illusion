import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .master_agent import run_master_pipeline
from .cache_db import init_db, get_cached_response, cache_response

load_dotenv()

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
TEAM_ID = os.getenv("TEAM_ID")
API_TOKEN = os.getenv("API_TOKEN")
API_ENDPOINT = os.getenv("API_ENDPOINT")

# Initialize database on startup
init_db()

app = FastAPI()

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:8800",
    "http://localhost",
    "http://localhost:8800",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/{company_name}")
def read_item(company_name: str):
    # Check cache first
    cached = get_cached_response(company_name)
    if cached:
        print(f"✓ Cache hit for {company_name}")
        return cached

    print(f"✗ Cache miss for {company_name}, fetching from master_agent...")
    response = run_master_pipeline(company_name)

    # Only cache if there's no error in the response
    if response.get("status") != "error":
        # Store in cache
        resolved_domain = response.get("search_result", {}).get("resolved_domain", "")
        cache_response(company_name, resolved_domain, response)
        print(f"✓ Cached response for {company_name}")
    else:
        print(f"✗ Error in response, skipping cache for {company_name}")

    return response
