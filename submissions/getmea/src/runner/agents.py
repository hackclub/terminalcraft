import requests
import json
import math

from config import config

from typing import TypedDict

from runner.collector import get_linux_flavor, search_duck_duck
from html2markdown.crawler import main as crawl


# Types
class MessageType(TypedDict):
    role: str
    content: str


class RoutingAgentResType(TypedDict):
    name: str
    description: str
    bestSource: str
    packageInstallCMD: str | None
    webSearchQuery: str | None


class SearchingAgentResType(TypedDict):
    bestUrl: str
    alternativeUrl: str


class ExtractingAgentResType(TypedDict):
    summary: str


class PlanningAgentStep(TypedDict):
    command: str
    description: str


class PlanningAgentResType(TypedDict):
    steps: list[PlanningAgentStep]
    canInstallProgram: bool


# Inference
class BasePrompt:
    model = config.getConfig()["models"]["planner"]

    def inference(
        self, messages: list[MessageType], double_json=False, reasoning=False
    ):
        req = requests.post(
            f"{config.getConfig()['openai']['base_url']}/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "response_format": {"type": "json_object"} if double_json else None,
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config.getConfig()['openai']['token']}",
            },
        )

        if req.status_code != 200:
            # Request failed
            # TODO: Retry 2 - 3 times
            raise Exception(f"Inference failed with model {self.model}: {req.text}")

        res = req.json()

        if double_json:
            return json.loads(res["choices"][0]["message"]["content"])
        else:
            return res["choices"][0]["message"]["content"]


# Agents
class RoutingAgent(BasePrompt):
    model = config.getConfig()["models"]["planner"]

    def run(self, program: str) -> RoutingAgentResType:
        # Get linux flavor
        flavor = get_linux_flavor()

        res = self.inference(
            [
                {
                    "role": "system",
                    "content": f"""You are a Linux system administration expert! The user will provide the name of a software, library, or program available on Linux.

Your task is to determine whether the software is available in the standard system package registry (such as dnf, apk, etc.) or if the user needs to install it manually by browsing the web (e.g., Bun, Deno, NVM [Node Version Manager]).
- Only state that the software is in the package registry if you are ABSOLUTLY certain it is available.
- If you are unsure, ALWAYS DEFAULT to web research as the preferred installation method.
- Some modern software like Deno or Bun are not in the system package manages, USE A WEBSEARCH FOR THEM!

For context, the system is running the following Linux distribution:
{flavor} 

Please respond only in the following JSON format (without a code block, just raw JSON):
{{
  "name": "<software name>",
  "description": "<short description of the software>",
  "bestSource": "PackageRegistry" | "WebResearch",
  "packageInstallCMD"?: "<command to install on the given linux distro if in package registry, always add a -y flag or similar for automatic installation>",
  "webSearchQuery"?: "<simple google search query to find the installation page of the program, example: Deno installation>"
}}""",
                },
                {"role": "user", "content": program},
            ],
            double_json=True,
            reasoning=True,
        )

        return res


class SearchingAgent(BasePrompt):
    model = config.getConfig()["models"]["planner"]

    def run(self, routing_res: RoutingAgentResType) -> SearchingAgentResType:
        # Search DuckDuckGo
        results = search_duck_duck(routing_res["webSearchQuery"])

        res = self.inference(
            [
                {
                    "role": "system",
                    "content": f"""You are a Google search agent expert! The user will provide with 5 search results for the query {routing_res['webSearchQuery']}.

Your task is to determine the best and second best search result matching the query given above.
- The query will be about installing a given software. Please prefer the official software sources above any third party ones.
- Sometimes the website description can be off, use common sense and argue in your thought about the best and second best match.


Please respond only in the following JSON format (without a code block, just raw JSON):
{{
  "bestUrl": "<best matching result>",
  "alternativeUrl": "<alternative result if the first isn't successful>"
}}""",
                },
                {"role": "user", "content": results},
            ],
            double_json=True,
            reasoning=True,
        )

        return res


class ExtractingAgent(BasePrompt):
    model = config.getConfig()["models"]["scraper"]

    def run(
        self, search_res: SearchingAgentResType, program_name: str
    ) -> ExtractingAgentResType:
        # Scrape website
        scraped = crawl(search_res["bestUrl"])

        # Run for times with a context window of ~4000 characters
        SPLIT_SIZE = 6000
        SPLIT_OVERLAP = 200
        count = 0

        result: ExtractingAgentResType = {}

        while count < 4:
            split = ""

            if len(scraped) < (SPLIT_SIZE + SPLIT_OVERLAP):
                split = scraped
                count = math.inf
            else:
                split = scraped[: (SPLIT_SIZE + SPLIT_OVERLAP)]
                scraped = scraped[(SPLIT_SIZE - SPLIT_OVERLAP) :]

            res = self.inference(
                [
                    {
                        "role": "system",
                        "content": f"""You are a website scraper expert agent! The user will provide you with a piece of a scraped website and should extract intel regarding how to install {program_name} on Linux.

If the snippet contained useful information regarding the query you should write a short summary about what you found.
- We are searching for direct installation instructions for linux, no bla bla 
- Ideally you would find something concert like `curl -f https://zed.dev/install.sh | sh`


Please respond only in the following JSON format (without a code block, just raw JSON):
{{
  "foundSomething": "<boolean>",
  "summary"?: "<short writeup about what you found, if you found something.>"
}}""",
                    },
                    {"role": "user", "content": split},
                ],
                double_json=True,
                reasoning=False,
            )

            if res["foundSomething"]:
                result["summary"] = res["summary"]
                break

            count += 1

        return result


class PlanningAgent(BasePrompt):
    model = config.getConfig()["models"]["planner"]

    def run(
        self,
        extraction_res: ExtractingAgentResType,
        program_name: str,
        search_query: str,
        searched_url: str,
    ) -> PlanningAgentResType:
        # Get linux flavor
        flavor = get_linux_flavor()

        res = self.inference(
            [
                {
                    "role": "system",
                    "content": f"""You are a Linux system administration expert! You are installing {program_name} on a linux pc for the normal user (not root, unless of course needed by software). 
                    
You have already decided that you need more information for installing this software and have kicked of a websearch with the following result:
Search Query: {search_query}
Website: {searched_url}
Extracted information: {extraction_res['summary']}


Please respond only in the following JSON format (without a code block, just raw JSON):
{{
  "steps": [
        {{
            "command": "<shell command to run, debate if adding a -y flag or similar for a automatic installation works for the command. Ideally the installation would be totally automated>",
            "description": "<short description of the command>"
        }}
      ],
  "canInstallProgram": <bool, wether you are confident the you have enough information to successfully install the software>  
}}""",
                },
                {
                    "role": "user",
                    "content": f"""Given this information please now formulate the next steps for the successful installation of the program.

                    For context, the system is running the following Linux distribution:
{flavor} 
""",
                },
            ],
            double_json=True,
            reasoning=True,
        )

        return res
