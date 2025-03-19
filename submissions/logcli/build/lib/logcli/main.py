import argparse
from logcli.utils.auth import login, logout ,register
from logcli.utils.logs import upload_log, get_logs, view_log, download_log

def main():
    parser = argparse.ArgumentParser(description="Flight Data Logger CLI")
    
    subparsers = parser.add_subparsers(dest="command")

    register_parser = subparsers.add_parser("register", help="Register a new user and login")
    register_parser.add_argument("name", help="User's full name")
    register_parser.add_argument("email", help="User email")
    register_parser.add_argument("password", help="User password")
    register_parser.add_argument("--role", help="User role (default: user)", default="user")

    # Login
    login_parser = subparsers.add_parser("login", help="Login to the system")
    login_parser.add_argument("email", help="User email")
    login_parser.add_argument("password", help="User password")

    # Logout
    subparsers.add_parser("logout", help="Logout from the system")

    # Upload log
    upload_parser = subparsers.add_parser("upload", help="Upload a flight log")
    upload_parser.add_argument("file_path", help="Path to the log file")
    upload_parser.add_argument("--metadata", help="Optional metadata (JSON string)", default=None)

    # Retrieve logs
    subparsers.add_parser("logs", help="Retrieve all logs")

    # View log
    view_parser = subparsers.add_parser("view-log", help="View details of a specific flight log")
    view_parser.add_argument("log_id", help="Log ID to view details")

    # Download log
    download_parser = subparsers.add_parser("download-log", help="Download a flight log file")
    download_parser.add_argument("log_id", help="Log ID of the file to download")
    download_parser.add_argument("output_path", nargs="?", default=None, help="Optional output file path")

    args = parser.parse_args()

    if args.command == "login":
        login(args.email, args.password)
    elif args.command == "register":
        register(args.name, args.email, args.password, args.role)
    elif args.command == "logout":
        logout()
    elif args.command == "upload":
        upload_log(args.file_path, args.metadata)
    elif args.command == "logs":
        get_logs()
    elif args.command == "view-log":
        view_log(args.log_id)
    elif args.command == "download-log":
        download_log(args.log_id, args.output_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

