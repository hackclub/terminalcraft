import sys
print(sys.argv)
for i in range(3):
    inp = input(f"i have {i} slices of galvanised square steel")
    print(f"{i}: {inp}")
raise Exception(f"{input()} is quite the nuisance")
