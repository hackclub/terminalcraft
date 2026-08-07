from args import ArgsType

from runner.planner import Planner

from sys import exit


def run(args: ArgsType):
    if len(args["args"]) != 1:
        print("Currently only one installation at once supported!")
        exit(-1)

    try:
        install(args["args"][0])
    except KeyboardInterrupt:
        exit(-1)


def install(program: str):
    # Create handler and try to create plan
    handler = Planner()
    plan = handler.plan(program)

    # Format & Print plan, wait for confirmation
    confirmation = plan.print_confirmation()

    if not confirmation:
        print("Exiting")
        exit(-1)

    # Install
    success, error = plan.execute()

    if success:
        print(f"\rDone! Successfully installed {plan.name}")
    else:
        print(f"\rError: " + error)
        exit(-1)
