from dotenv import load_dotenv
from strands import tool
from pathlib import Path

from langchain_valyu import ValyuSearchTool

import os

load_dotenv(Path('.env'))

VALYU_API_KEY = os.getenv("VALYU_API_KEY")

# Create search tool with configuration
search_tool = ValyuSearchTool(
    valyu_api_key=VALYU_API_KEY,
    # Optional: configure search parameters (can also be set per-call)
    # search_type="all",  # Search both proprietary and web sources
    # max_num_results=5,   # Limit results
    # relevance_threshold=0.5,  # Minimum relevance score
    # max_price=20.0  # Maximum cost in dollars
)