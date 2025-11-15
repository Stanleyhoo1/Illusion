import json
import os
import pathlib
from typing import Any, Dict, Optional


from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from draft_email import draft_emails
from random_data import generate_random_estate_data
from database import (
    create_session,
    get_session,
    init_db,
    save_survey_data,
    update_task_status,
)
from agents import get_post_death_checklist
from compute_agent import compute_figures
from search import search_agent
from langgraph_workflow import create_langgraph_workflow

load_dotenv()