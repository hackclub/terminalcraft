def setname(name: str) -> str:
  import json

  f = open(".data", "r+")
  data = json.load(f)
  data["name"] = name.strip().lower().replace(" ", "-")
  f.seek(0)
  global has_name
  has_name = True
  json.dump(data, f, indent=2)
  f.truncate()
  f.close()
  return data["name"]