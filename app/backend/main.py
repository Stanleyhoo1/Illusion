import json
import os
import pathlib
from typing import Any, Dict, Optional


from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langgraph_workflow import create_langgraph_workflow

load_dotenv()

VALYU_API_KEY = os.getenv("VALYU_API_KEY")
TEAM_ID = os.getenv("TEAM_ID")
API_TOKEN = os.getenv("API_TOKEN")
API_ENDPOINT = os.getenv("API_ENDPOINT")

