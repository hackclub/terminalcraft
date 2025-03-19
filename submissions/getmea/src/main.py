# Args for nuitka
# nuitka-project: --mode=onefile
# nuitka-project: --include-data-dir=./data=data
# nuitka-project: --output-filename=getmea.bin
# nuitka-project: --lto=no
# nuitka-project: --nofollow-import-to=playwright,litellm

from args import args, parser
from setup import setup
from runner.handler import run

from sys import platform, exit


# Entrypoint
if __name__ == "__main__":
    if platform != "linux" and platform != "linux2":
        # Currently only supported on linux (due to the nature of a linux package installation tool...)
        print("GetMeA currently only support linux")
        exit(-1)

    # CMD help
    if len(args["args"]) == 0:
        parser.print_usage()
        exit(-1)

    if len(args["args"]) == 1 and "help" in args["args"]:
        parser.print_help()
        exit(-1)

    # TODO: Updates -> Somehow include git commit hash in compiled build...
    # if len(args["args"]) == 1 and "update" in args["args"]:
    #    # Update installation
    #    update(args)
    if len(args["args"]) == 1 and "setup" in args["args"]:
        # Update installation
        setup(args)
    else:
        # Plan & run installation
        run(args)
