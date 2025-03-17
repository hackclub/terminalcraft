from openai import OpenAI
import requests
from typing import List
import json
import time
from sqlmodel import Session, select, and_
from models import ChatSession, ChatRecord
import statsd

def get_time_millis():
    return round(time.time() * 1000)

class SessionLimitExceeded(Exception):
    def __init__(self):
        super().__init__()

class SessionAlreadyExists(Exception):
    def __init__(self):
        super().__init__()

class LLMAssistant:
    def __init__(self, metrics: statsd.StatsClient, user_email: str, session_id: str, pg_engine):
        self.metrics = metrics
        self.user_email = user_email
        self.sprig_docs = self.load_sprig_docs()
        self.model_version = "gpt-3.5-turbo"
        self.session_id = session_id
        self.pg_engine = pg_engine

        with Session(self.pg_engine) as session:
            chat_session = session.exec(select(ChatSession).where(ChatSession.id == self.session_id)).first()
            if chat_session is None:
                if self.has_existing_sessions(): raise SessionLimitExceeded

                self.metrics.incr("start_session")
                # create a new chat session as it does not exist yet
                chat_session = ChatSession(
                    id=self.session_id,
                    user_email=self.user_email,
                )
                # create a new system prompt and messages iff the session passed does not exist yet
                chat_record = ChatRecord(
                    session_id=self.session_id,
                    model=self.model_version,
                    role="system",
                    content="Here is the sprig documentation" + "\n\n" + self.sprig_docs + "\n\n With the help of the documentation, you have become an expert in JavaScript and understand Sprig. With the help of this documentation, answer prompts in a concise way.",
                    timestamp=get_time_millis()
                )
                session.add(chat_session)
                session.add(chat_record)
                session.commit()
            else:
                if not chat_session.user_email == self.user_email: raise SessionAlreadyExists
                if chat_session.has_ended:
                    if not self.has_existing_sessions():
                        chat_session.has_ended = False

                        # update the status of the session in the database
                        session.add(chat_session)
                        session.commit()
                    else:
                        raise SessionLimitExceeded
                self.metrics.incr("continue_session")

    # use this method to raise a SessionLimitExceeded error if the current user has more than a single running session
    def has_existing_sessions(self):
        with Session(self.pg_engine) as session:
            chat_sessions_by_user = session.exec(select(ChatSession).where(and_(ChatSession.has_ended == False, ChatSession.user_email == self.user_email))).all()

            return len(chat_sessions_by_user) > 0

    @staticmethod
    def build_code_prompt(self, code: str, error_logs: str = ""):
        prompt = (
            "Here is a piece of code: "
            + f"\n ```\n{code} \n```"
            + "\n it is showing me these errors"
            + f"\n```\n{error_logs} \n ```"
            + "\n identify the issue in the code and suggest a fix. write the full code with the issue fixed."
        )
        return prompt

    def load_sprig_docs(self) -> str:
        sprig_docs_url = (
            "https://raw.githubusercontent.com/hackclub/sprig/main/docs/docs.md"
        )
        try:
            sprig_docs = requests.get(sprig_docs_url)
        except requests.exceptions.ConnectionError:
            self.metrics.incr("errors.load_sprig_docs")
        return str(sprig_docs.content)

    """
    The response returned by ChatGPT contains code wrapped in blocks by backticks
    with the language specified at the end of the opening three backticks
    ```js
    ```

    This function takes advantage of this information to split the completion text
    by three backticks.

    If we start counting from 1, the code within the backticks will always fall
    at even number indices.

    So, we can get only the text at those indices knowing that it's a block of code from the completion.

    We then slice away the text upto the first new line as they're usually the language specifier.

    """

    def get_code_blocks(self, source: str, delimiter: str = "```") -> List[str]:
        results = []
        for i, x in enumerate(source.split(delimiter)):
            if (i + 1) % 2 != 0:
                continue
            # remove the dangling language specifier
            first_newline = x.find("\n")
            results.append(x[first_newline + 1 :])
        return results

    # this method should be overriden in the implementation
    def get_completion(self, messages) -> str:
        return ""

    def chat_completion(self, message: str):
        messages = self.load_previous_messages()

        completion = self.get_completion(messages + [{
            "role": "user",
            "content": message
        }])

        completion_message = completion.get("message")

        new_messages = [
            {
                "role": "user",
                "content": message
            },
            {
                "role": "assistant",
                "content": completion_message
            }
        ]

        # add the newest messages as record into the database
        self.save_messages(new_messages)

        return completion_message

    def load_previous_messages(self):
        messages = []
        with Session(self.pg_engine) as session:
            chat_records = session.exec(
                select(ChatRecord).where(ChatRecord.session_id == self.session_id).order_by(ChatRecord.timestamp)
            ).all()
        for chat_record in chat_records:
            messages.append({
                "role": chat_record.role,
                "content": chat_record.content
            })
        return messages

    def save_messages(self, messages: List):
        with Session(self.pg_engine) as session:
            for message in messages:
                new_record = ChatRecord(
                    session_id=self.session_id,
                    model=self.model_version,
                    role=message.get("role", "user"),
                    content=message.get("content", ""),
                    timestamp=get_time_millis()
                )
                session.add(new_record)
                session.commit()

class ChatGPTAssistant(LLMAssistant):
    def __init__(self, metrics: statsd.StatsClient, user_email: str, session_id: str, pg_engine, openai_api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__(metrics=metrics, user_email=user_email, session_id=session_id, pg_engine=pg_engine)
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.model_version = model

    def get_completion(self, messages):
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model_version, messages=messages
            )

            result = {
                "message": response.choices.pop().message.content,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            self.metrics.incr("success.generate_response")
            return result
        except:
            self.metrics.incr("errors.generate_response")


class OllamaAssitantModel(LLMAssistant):
    def __init__(
        self,
        metrics: statsd.StatsClient,
        user_email: str,
        session_id: str, pg_engine,
        model: str = "llama2",
        ctx_window: int = 4096,
        OLLAMA_SERVE_URL: str = "http://127.0.0.1:11434",
    ):
        super().__init__(metrics=metrics, user_email=user_email, session_id=session_id, pg_engine=pg_engine)
        self.generate_endpoint = f"{OLLAMA_SERVE_URL}/api/generate"
        self.chat_endpoint = f"{OLLAMA_SERVE_URL}/api/chat"
        self.model_version = model
        self.ctx_window = ctx_window

    def generate_response(self, prompt: str):
        body = {
            "model": self.model_version,
            "prompt": prompt,
            "options": {
                "num_ctx": self.ctx_window,
            },
        }
        try:
            # ollama will return to use a stream of set of responses from the model
            responses = requests.post(self.generate_endpoint, data=json.dumps(body)).content
            responses = responses.decode("utf-8")

            # here we transform the response into a single string for further processing
            response_bulk = [
                json.loads(response_str).get("response")
                for response_str in responses.splitlines()
            ]
            response_bulk = "".join(response_bulk)

            self.metrics.incr("success.generate_response")
            return response_bulk
        except requests.exceptions.ConnectionError:
            self.metrics.incr("errors.generate_response")

    def get_completion(self, messages):
        body = {
            "model": self.model_version,
            "messages": messages,
            "options": {
                "num_ctx": self.ctx_window,
            },
        }
        try:
            responses = requests.post(self.chat_endpoint, data=json.dumps(body)).content
            responses = responses.decode("utf-8")

            # the last item in a ollama response is the response summary including token count, duration etc
            response_summary = json.loads(responses[-1])
            token_counts = {
                "prompt_tokens": response_summary.get("eval_count"),
                "completion_tokens": response_summary.get("prompt_eval_count"),
                "total_tokens": response_summary.get("eval_count") + response_summary.get("prompt_eval_count")
            }
            response_bulk = [
                json.loads(response_str).get("message").get("content")
                for response_str in responses.splitlines()
            ]
            response_bulk = "".join(response_bulk)

            self.metrics.incr("success.generate_response")
            return { "message": response_bulk } | token_counts
        except:
            self.metrics.incr("errors.generate_response")
