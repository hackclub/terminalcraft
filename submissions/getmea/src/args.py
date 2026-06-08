import argparse

from typing import TypedDict, List


class ArgsType(TypedDict):
    verbose: bool
    yes: bool
    args: List[str]


parser = argparse.ArgumentParser(
    prog="GetMeA",
    description="AI automated software installation",
    usage="getmea [-h] [-v] [-y] software",
    epilog="This product includes software developed by UncleCode (https://x.com/unclecode) as part of the Crawl4AI project (https://github.com/unclecode/crawl4ai).",
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Enable verbose logging"
)
parser.add_argument(
    "-y", "--yes", action="store_true", help="Skip confirmation - Not recommended"
)
parser.add_argument("args", nargs="*", help="Software to install")

args: ArgsType = vars(parser.parse_args())
