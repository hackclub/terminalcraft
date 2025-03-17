from fastapi import FastAPI, status, Response
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from ollama import ChatGPTAssistant, SessionLimitExceeded, SessionAlreadyExists, get_time_millis
from models import ChatSession, ChatRecord
from dotenv import load_dotenv
from sqlmodel import create_engine, SQLModel, Session, select, and_
import statsd
import os
import time
import datetime

load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
PG_DATABASE_URL = os.environ["PG_DATABASE_URL"]
GRAPHITE_HOST = os.environ["GRAPHITE_HOST"]
GRAPHITE_HOST_PORT = os.environ["GRAPHITE_HOST_PORT"]

app = FastAPI()
pg_engine = create_engine(PG_DATABASE_URL)
metrics = statsd.StatsClient(host=GRAPHITE_HOST, port=GRAPHITE_HOST_PORT, prefix="production.llmapi")

# create all tables
SQLModel.metadata.create_all(pg_engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sprig.hackclub.com",
        "http://localhost:3000",
        "https://sprig-git-feat-send-code-on-change.hackclub.dev",
        "https://sprig.hackclub.com",
        "*.hackclub.com",
        "*.hackclub.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def _hello_world():
    return "Hello World"

@app.post("/generate")
async def _generate_response(req: Request, response: Response):
    metrics.incr("generate")

    # time it starts handing a request
    start_time = time.time()
    body = await req.json()

    user_email = body.get("email", None)
    session_id = body.get("session_id", None)
    message = body.get("message", None)

    if user_email is None or session_id is None or message is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "success": False,
            "error":
            f"{user_email} is not a valid email" if user_email is None else ""      +
            f"{session_id} is not a valid session_id" if session_id is None else "" +
            f"{message} is not a valid message" if message is None else ""
        }

    with Session(pg_engine) as session:
        chat_session = session.exec(select(ChatSession).where(ChatSession.id == session_id)).first()

    try:
        model = ChatGPTAssistant(metrics=metrics, user_email=user_email, session_id=session_id, pg_engine=pg_engine, openai_api_key=OPENAI_API_KEY)
    except SessionLimitExceeded:
        metrics.incr("session_limit_exceeded")
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return { "success": False, "error": "You can only have one session running at a time." }
    except SessionAlreadyExists:
        metrics.incr("session_exists")
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return { "success": False, "error": "This session already exists and is owned by another user." }

    response = {}

    prompt_response = model.chat_completion(message)
    code_blocks = model.get_code_blocks(prompt_response)

    response["raw"] = prompt_response
    response["codes"] = code_blocks

    total_time = time.time() - start_time
    total_time = time.time() = start_time

    # log time it took to handle request
    metrics.timing("generate_response.timed", total_time)

    response_out = response | { "success": True }
    return response_out

@app.post("/end-session")
async def _end_chat_session(req: Request):
    body = await req.json()

    session_id = body.get("session_id")
    with Session(pg_engine) as session:
        chat_session = session.exec(select(ChatSession).where(ChatSession.id == session_id)).first()
        if chat_session is not None:
            chat_session.has_ended = True

            session.add(chat_session)
            session.commit()
    metrics.incr("end_session")
    return { "success": True }

@app.get("/end-stale-sessions")
async def _end_stale_session():
    with Session(pg_engine) as session:
        running_sessions = session.exec(select(ChatSession).where(ChatSession.has_ended == False)).all()
        for running_session in running_sessions:
            now = get_time_millis()

            # get all chat records for the current session id
            records = session.exec(select(ChatRecord).where(ChatRecord.session_id == running_session.id).order_by(ChatRecord.timestamp)).all()

            last_record_timestamp = records[-1].timestamp
            minute = 1000 * 60
            time_diff = (now - last_record_timestamp) / minute

            # end all sessions that are older than 2 minutes
            if time_diff >= 2:
                chat_session = session.exec(select(ChatSession).where(ChatSession.id == running_session.id)).first()
                chat_session.has_ended = True

                session.add(chat_session)
                session.commit()
    metrics.incr("end_stale_sessions")
    return { "success": True }
