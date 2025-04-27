def info():
  import json
  import platform
  from datetime import datetime

  f = open(".data", "r+")
  data = json.load(f)
  print("GemTerm 0.1.0 running on", platform.version())
  print()
  print("Welcome to GemTerm! Type 'help' for a list of commands.")
  print()
  if "last_login" in data:
    print("Last login:", data["last_login"])
  data["last_login"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S")
  f.seek(0)
  json.dump(data, f, indent=2)
  f.truncate()
  f.close()
