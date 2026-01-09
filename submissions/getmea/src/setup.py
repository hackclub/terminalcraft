import os
import sys
import shutil
import stat

from args import ArgsType

from config import CONFIG_DIR, config


def setup(args: ArgsType):
    # Copy self to .getmea
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        shutil.copyfile(
            os.path.join(os.path.dirname(sys.argv[0]), "getmea.bin"),
            CONFIG_DIR / "getmea.bin",
        )

        # Make executable
        st = os.stat(CONFIG_DIR / "getmea.bin")
        os.chmod(CONFIG_DIR / "getmea.bin", st.st_mode | stat.S_IEXEC)
    except Exception as err:
        print(f"Unable to copy build executable to {CONFIG_DIR}: {err}")

    # Show user what to add to .bashrc
    print(f"GetMeA was installed to {CONFIG_DIR}")

    # Initiate config
    res = config.getConfig(silent=True)

    if res == False:
        print(
            f"Please add your OpenAI API compatible base_url and token to {CONFIG_DIR}/config.toml"
        )

    print("Manually add the following to the end of your .bashrc:")
    print("""  alias "getmea"="~/.getmea/getmea.bin" """)

    print("Run 'getmea --help' to get started")

    sys.exit(0)
