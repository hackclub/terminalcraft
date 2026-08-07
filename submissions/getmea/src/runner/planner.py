# Target flow
# Calls:   1                        2                                 3                                                              4                                              5
# Formulate search query  ->  Parse website    ->   Create plan, check if further research required    ->  Parse two additional sites with one target query -> Back to planner to create final installation plan
import sys
import subprocess
import select

from runner.agents import RoutingAgent, SearchingAgent, ExtractingAgent, PlanningAgent
from typing import TypedDict, Literal

from utils.spinner import spinner


# Types
class PlanStepType(TypedDict):
    type: Literal["command"]
    value: str
    description: str


class Plan:
    name: str
    description: str

    steps: list[PlanStepType] = []

    def __init__(self, program, description):
        self.name = program
        self.description = description

    def add_step(self, type, value, description):
        self.steps.append({"value": value, "type": type, "description": description})

    def util_ask_y_n(self, question: str, default: bool = False) -> bool:
        answers = {"yes": True, "y": True, "no": False, "n": False}

        while True:
            sys.stdout.write(f"{question} [y/n] ")
            choice = input().lower()
            if choice == "":
                return default
            elif choice in answers:
                return answers[choice]

    def print_confirmation(self):
        # Printing
        print(f"Program name: {self.name}")
        print(f"Description: {self.description}")
        print("Installation steps:")

        for step in self.steps:
            if step["type"] == "command":
                print(f"- Run: {step['value']}")
                print(f"  Description: {step['description']}")

        return self.util_ask_y_n("Do you want to execute these steps?")

    def execute(self):
        for step in self.steps:
            print(f"- Running: {step['value']}")

            process = subprocess.Popen(
                step["value"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True,
            )
            try:
                while process.poll() is None:
                    # Check process stdout and sys stdin for new outputs/inputs every 0.1s
                    readable, _, _ = select.select(
                        [process.stdout, sys.stdin], [], [], 0.1
                    )

                    # If output from the process -> Print!
                    if process.stdout in readable:
                        line = process.stdout.readline()

                        sys.stdout.write(f"  {line}")
                        sys.stdout.flush()

            except:
                return (
                    False,
                    f"Internal error",
                )

            # TODO: Feed into LLM to try to fix the issue ?
            code = process.wait()

            if code != 0:
                return (
                    False,
                    f"Error running command '{step['value']}', exit code '{code}'",
                )

        return (True, None)


class Planner:
    def plan(self, program: str) -> Plan:
        """Create plan to download and install the given software"""
        spinner.start()

        # First: Decide wether it's a package that can be installed with dnf/etc or if we need to research
        routing_res = RoutingAgent().run(program)

        plan = Plan(routing_res["name"], routing_res["description"])

        # Check if only a package install
        if routing_res["bestSource"] == "PackageRegistry":
            plan.add_step(
                "command",
                routing_res["packageInstallCMD"],
                f"Using system package registry to install {routing_res['name']}",
            )
            spinner.stop()
            return plan

        # DuckDuck the search query
        spinner.message = f"Searching the web: {routing_res['webSearchQuery']}"
        search_res = SearchingAgent().run(routing_res)

        # Try to extract any hints from website
        spinner.message = f"Inspecting '{search_res['bestUrl']}'"
        extraction_res = ExtractingAgent().run(search_res, routing_res["name"])

        # Construct plan
        spinner.message = f"Planning"

        planning_res = PlanningAgent().run(
            extraction_res,
            routing_res["name"],
            routing_res["webSearchQuery"],
            search_res["bestUrl"],
        )

        spinner.stop()

        # Add to plan
        for step in planning_res["steps"]:
            plan.add_step("command", step["command"], step["description"])

        return plan
