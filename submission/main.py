import sys

'''if __name__!="__main__":
    raise RuntimeError("This script should be run directly and not imported as a module.")'''

# make sure console argument are valid
if len(sys.argv)!=3:
    print("Two Command Line Arguments Expected: \"buzzerTone.py <mode> <filename>\"")
    sys.exit()
if sys.argv[1]=="c":
    import compile
    if compile.compile(sys.argv[2]):
        print("\nAn error encountered, program stoped.")
    else:
        print("\nCompile success, program exited.\n")
elif sys.argv[1]=="p":
    import play
    if play.play(sys.argv[2]):
        print("\nAn error encountered, program stoped.")
    else:
        print("\nSound sequence finished, program exited.\n")
else:
    print("")

