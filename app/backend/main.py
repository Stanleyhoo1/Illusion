import os

from dotenv import load_dotenv
from fastapi import FastAPI

from .agent import master_agent

load_dotenv()

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
TEAM_ID = os.getenv("TEAM_ID")
API_TOKEN = os.getenv("API_TOKEN")
API_ENDPOINT = os.getenv("API_ENDPOINT")

app = FastAPI()


@app.get("/{company_name}")
def read_item(company_name: str):
    return master_agent(company_name)
