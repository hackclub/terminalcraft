import requests
import os
import time
from logcli.utils.config import BASE_URL, load_token

def upload_log(file_path, metadata=None):
    token = load_token()
    if not token:
        print("\n🚫 🔒 \033[91mYou must be logged in to upload logs!\033[0m 🔒 🚫")
        print("\n💡 Run: \033[96mlogcli login\033[0m to authenticate.\n")
        return

    if not os.path.exists(file_path):
        print("\n📂 ❌ \033[91mFile not found:\033[0m", file_path)
        print("⚠️  Please check the path and try again.\n")
        return

    url = f"{BASE_URL}/api/logs/upload"
    cookies = {"token": token}
    
    print("\n📡 \033[93mUploading log file...\033[0m 🌍\n")

    # 🌀 Cool Upload Animation
    animation = ["📤▒▒▒", "📤█▒▒", "📤██▒", "📤███"]
    for frame in animation:
        print(f"\r{frame} Uploading...", end="", flush=True)
        time.sleep(0.5)

    files = {"file": open(file_path, "rb")}
    data = {"metadata": metadata} if metadata else {}

    response = requests.post(url, cookies=cookies, files=files, data=data)

    try:
        res_json = response.json()
    except requests.exceptions.JSONDecodeError:
        res_json = {}

    # ✅ Fix: Check for the success message
    if "log" in res_json and res_json.get("message") == "Log uploaded successfully":
        print("\n\n🎉✅ \033[92mLog uploaded successfully!\033[0m 🚀")

        print(f"""
        ┌─────────────────────────────────────────────┐
        │ 🎊✨ \033[92mUPLOAD SUCCESS\033[0m ✨🎊
        ├─────────────────────────────────────────────┤
        │ 📂  \033[96mFile Stored at:\033[0m
        │    {res_json["log"]["file"]}
        ├─────────────────────────────────────────────┤
        │ 🆔  \033[93mUpload ID:\033[0m
        │    {res_json["log"]["_id"]}
        ├─────────────────────────────────────────────┤
        │ 🗓️   \033[94mUploaded on:\033[0m
        │    {res_json["log"]["date"]}
        ├─────────────────────────────────────────────┤
        │ 🚀 \033[92mYou can now view the log online!\033[0m
        └─────────────────────────────────────────────┘
        """)

    else:
        print("\n❌ \033[91mUpload failed!\033[0m")
        print("\n📜 Response:\n", response.text)
        print("\n🚀 Try again later or check your API settings!\n")


def get_logs():
    token = load_token()
    cookies = {"token": token} if token else {}

    print(r"""
    ╔══════════════════════════════════════════╗
    ║   🚀 Flight Data Logger - Mission Logs   ║
    ╠══════════════════════════════════════════╣
    ║    🌍 Tracking the skies, one log at a time ✈️   ║
    ╚══════════════════════════════════════════╝
    """)

    print("📡 Connecting to the flight log database...\n")

    response = requests.get(f"{BASE_URL}/api/logs", cookies=cookies)
    
    try:
        data = response.json()
    except requests.JSONDecodeError:
        print("\n💥 ERROR: Failed to decode JSON response!\n")
        return

    if isinstance(data, dict) and "message" in data:
        print(f"\n⚠️ API ERROR: {data['message']}\n")
        return

    if isinstance(data, dict) and "logs" in data:
        logs = data["logs"]
    else:
        print("\n🚨 Unexpected response format! Check API response.\n")
        return

    if isinstance(logs, list) and logs:
        print("\n🌍 Flight Logs Retrieved:\n")
        print("═══════════════════════════════════════════════════════════════════════════════")
        for log in logs:
            log_id = log.get("_id", "Unknown ID")  
            uploader_id = log.get("user", "Unknown User")  
            file_url = log.get("file", "No file URL provided")
            date = log.get("date", "Unknown Date")

            print(f"""
            ┌───────────────────────────────────────────────┐
            │ 🆔 Log ID     : {log_id}              
            │ 📂 File       : {file_url}       
            │ 👨‍✈️ Uploaded by: {uploader_id} (User ID)    
            │ 🕒 Date       : {date}        
            └───────────────────────────────────────────────┘
            """)

        print("\n🎉✅ Log retrieval complete! Fly high, pilot! ✈️\n")

    else:
        print(r"""
        🌥️  ────────────────────────────  
        🌍  No flight logs found.       
        ✈️  The skies are clear!       
        ────────────────────────────  
        """)


def view_log(log_id):
    token = load_token()
    cookies = {"token": token} if token else {}

    print(r"""
    ╔══════════════════════════════════════════╗
    ║   🔍 Flight Log Details - Mission View   ║
    ╚══════════════════════════════════════════╝
    """)

    response = requests.get(f"{BASE_URL}/api/logs/{log_id}", cookies=cookies)

    if response.status_code != 200:
        print(f"\n❌ Error: Unable to fetch log (HTTP {response.status_code})\n")
        print(f"🔍 Response: {response.text}\n")
        return

    try:
        data = response.json()
        log = data.get("log", {})  # Extract the actual log details
    except requests.JSONDecodeError:
        print("\n💥 ERROR: Failed to decode JSON response!\n")
        return

    if not log:
        print("\n⚠️ No log details found!\n")
        return

    log_id = log.get("_id", "Unknown ID")
    file_url = log.get("file", "No file URL provided")
    uploader = log.get("user", {}).get("name", "Unknown User")
    uploader_email = log.get("user", {}).get("email", "Unknown Email")
    date = log.get("date", "Unknown Date")

    print(f"""
        🆔 Log ID       : {log_id}
        📂 File URL     : {file_url}
        👨‍✈️ Uploaded by : {uploader} ({uploader_email})
        🕒 Date         : {date}
        ───────────────────────────────────────────
    """)

import requests
import os
import sys
import time

def download_log(log_id, output_path=None):
    token = load_token()
    cookies = {"token": token} if token else {}

    response = requests.get(f"{BASE_URL}/api/logs/{log_id}", cookies=cookies)

    if response.status_code != 200:
        print(f"\n❌ ERROR: Failed to fetch log {log_id}\n📜 Details: {response.text}\n")
        return

    log_data = response.json().get("log", {})
    file_url = log_data.get("file")
    
    if not file_url:
        print("\n🚨 OOPS! No file URL found for this log! 🚨\n")
        return

    # Extract original filename from URL
    filename = os.path.basename(file_url)
    
    # Use provided output_path or default filename
    save_path = output_path if output_path else filename  

    # Fancy Header
    print("\n" + "=" * 50)
    print("🔻 FLIGHT LOG DOWNLOADER 🔻")
    print("=" * 50 + "\n")

    print(f"🎯 Fetching log: {log_id}")
    print(f"📂 Destination: {save_path}\n")
    
    # Simulated Download Animation
    sys.stdout.write("📡 Downloading: ")
    sys.stdout.flush()
    for _ in range(10):
        sys.stdout.write("⬇️ ")
        sys.stdout.flush()
        time.sleep(0.2)
    print("\n")

    # Download file
    file_response = requests.get(file_url, stream=True)
    with open(save_path, "wb") as file:
        for chunk in file_response.iter_content(chunk_size=1024):
            file.write(chunk)

    # Success message with ASCII Art
    print("\n🚀 DOWNLOAD COMPLETE! 🚀\n")
    print(f"🎉 Log successfully saved as: 🗂️  {save_path}\n")
    print("=" * 50)

