import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .master_agent import run_master_pipeline

load_dotenv()

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
TEAM_ID = os.getenv("TEAM_ID")
API_TOKEN = os.getenv("API_TOKEN")
API_ENDPOINT = os.getenv("API_ENDPOINT")


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
    return run_master_pipeline(company_name)
