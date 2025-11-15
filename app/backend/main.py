import os
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
TEAM_ID = os.getenv("TEAM_ID")
API_TOKEN = os.getenv("API_TOKEN")
API_ENDPOINT = os.getenv("API_ENDPOINT")

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
