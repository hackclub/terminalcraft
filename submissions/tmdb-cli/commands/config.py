import os

def set(args):
    env_file = ".env"
    env_vars = {}

    # Get the existing vars if the file exists
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            for line in f:
                key, value = line.strip().split("=", 1)
                env_vars[key] = value

    if args.set == "region":
        env_vars["REGION"] = args.value
        print(f"Set to {args.value}")
    elif args.set == "base_url":
        env_vars["BASE_URL"] = args.value
        print(f"Set to {args.value}")
    elif args.set == "img_url":
        env_vars["IMG_URL"] = args.value
        print(f"Set to {args.value}")
    elif args.set == "api_key":
        env_vars["API_KEY"] = args.value
        print(f"Set to {args.value}")

    with open(env_file, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")