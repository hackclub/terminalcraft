def getname():
  import json

  f = open(".data", "r")
  data = json.load(f)
  f.close()
  if data["name"]:
    print(data["name"])
  else:
    print("You don't have a name set. Please set one using the 'setname' command.")
