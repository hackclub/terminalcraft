from fastapi import FastAPI
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

LLM_SERVICE_URL = os.environ["LLM_SERVICE_URL"]

@app.on_event("startup")
def close_stale_sessions():
    requests.get(f"{LLM_SERVICE_URL}/end-stale-sessions")