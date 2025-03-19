import os
import sys
import shutil


from args import ArgsType

from config import CONFIG_DIR, config


def setup(args: ArgsType):
    # Copy self to .getmea
    os.makedirs(CONFIG_DIR, exist_ok=True)
    shutil.copyfile(
        os.path.join(os.path.dirname(sys.argv[0]), "getmea.bin"),
        CONFIG_DIR / "getmea.bin",
    )

    # Show user what to add to .bashrc
    print(f"GetMeA was installed to {CONFIG_DIR}")
    print(f"Please add your OpenAI API base_url and token to {CONFIG_DIR}/config.toml")
    print("Manually add the following to the end of your .bashrc:")
    print("""  alias "getmea"="~/.getmea/getmea.bin" """)
    print("Run 'getmea --help' to get started")

    # Initial config
    config.getConfig()
    sys.exit(0)
