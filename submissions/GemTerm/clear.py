def clear():
  import platform
  from os import system

  z = platform.system()
  if z == "Windows":
    system("cls")
  elif z == "Darwin" or z == "Linux":
    system("clear")
  else:
    print("Unsupported platform")
