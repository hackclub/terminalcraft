"""program written by e^pi*i+1=0 i.e. Jakub"""

import random as rnd
import math
import argparse as arg

parser = arg.ArgumentParser(description="Miller-Rabin primality test implementation in Python.")

parser.add_argument("type", help="specifies type of test; use 0 to manualy test a base; use 1 to randomly test a bunch of bases; use 2 to make \
a deterministic test, assuming that extended riemann hypothesis is true or for numbers less than 3317044064679887385961980, its true without this hypothesis;\
 use 3 to calculate pi(x)-pi(y) (its inclusive with those bounds); use 4 to find next primes from a given number")

parser.add_argument("-f", "--fast", action="store_true", help="use fast mode, which will not print intermediate results,\
                    on example it will not list primes counted in 3rd mode, it will not show progress, and it will stop when any witness is found")

test0 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

args = parser.parse_args()

test = args.type + "f" if args.fast else args.type

def digits(string):
    digit_list = []
    for char in string:
        if char.isdigit():
            digit_list.append(int(char))
    number = 0
    power = len(digit_list)-1

    for digit in digit_list:
        number += digit*pow(10, power)
        power -= 1
    return number


def mil_rab(n, a):

    if n == 2:
        return [True, 1]

    if n % 2 == 0:
        return [False, 2]

    d = n-1
    s = 0

    while (d % 2 == 0):
        d = d//2
        s = s+1

    x = (pow(a, d, n))
    y = 1

    for r in range(0, s):
        y = pow(x, 2, n)

        if (y == 1 and x != 1 and x != n-1):
            return [False, math.gcd(x - 1, n)]
        x = y

    if y != 1:
        return [False, 1]

    return [True, 1]


def mil(n, fast=False):

    if n == 2:
        return [False, [2], [2]]

    witnesses = []
    divisors = []
    com = False

    if n > 3317044064679887385961980:
        up = math.ceil(2*pow(math.log(n), 2))
        testlist = list(range(2, up))
    else:
        testlist = test0

    for base in testlist:
        if base < n:
            a = mil_rab(n, base)
        if a[0] == False and fast:
            if a[1] not in divisors:
                divisors.append(a[1])
            witnesses.append(base)
            com = True
            break

        elif a[0] == False:
            com = True
            if a[1] > 1:
                if a[1] not in divisors:
                    divisors.append(a[1])
            else:
                witnesses.append(base)

    witnesses.sort()
    divisors.sort()

    return [com, witnesses, divisors]


while True:
    if test == "0" or test == "0f":
        base = digits(input("what base?: "))
        while base < 2:
            base = digits(input("what base?: "))
        
        prime = digits(input("what number?: "))
        while prime < 2:
            prime = digits(input("what number?: "))

        a = mil_rab(prime, base)
        print("")
        
        if a[0] == False:
            if a[1] > 1:
                print(str(prime) + " is composite, multiple of: " +
                      str(a[1]) + " \n" + str(base) + " is the witness for the compositeness.\n")
            else:
                print(str(prime) + " is composite, divisor unknown \n" +
                      str(base) + " is the witness for the compositeness.\n")
        else:
            print(str(prime) + " is strong probable prime to base: " +
                  str(base) + "\n")

    if test == "1" or test == "1f":
        rep = digits(
            input("how many times (its enough to test 1+prime//4 times): "))
        while rep < 1:
            rep = digits(
                input("how many times (its enough to test 1+prime//4 times): "))
        
        
        prime = digits(input("what number?: "))
        while prime < 2:
            prime = digits(input("what number?: "))
        
        print("")

        tested = []
        witnesses = []
        divisors = []
        com = False

        if rep > prime-2:
            rep = prime-2

        if prime < pow(2, 63):
            rndlist = rnd.sample(range(2, prime), rep)
        else:
            if rep > 1+prime//2:
                rep = 1+prime//2
            rndlist = [rnd.randint(2, prime) for _ in range(0, rep)]

        for n in range(0, rep):
            a = mil_rab(prime, rndlist[n])
            tested.append(rndlist[n])

            if a[0] == False:
                com = True
                if a[1] > 1:
                    if a[1] not in divisors:
                        divisors.append(a[1])
                witnesses.append(rndlist[n])
                if test == "1f":
                    break
            if test != "1f":
                print(".", end="")
        
        if test != "1f":
            print("\n")

        tested.sort()
        witnesses.sort()
        divisors.sort()
        if com == False:
            if rep > (prime//4 + 1) or prime < 10:
                print(str(prime) + " is prime\n")
            else:
                if rep > pow(2, 12):
                    rep = 2048
                else:
                    print(str(prime) + " is strong probable prime to bases: " + str(tested) +
                          "\n    chances of it being composite are: 1/" + str(pow(4, rep)) + "\n")
        else:
            if len(divisors) >= 1:
                if test == "1f":
                    print(str(prime) + " is composite and divisible by: " + str(divisors) +
                          ";\n   " + str(witnesses[0]) + " is the witnesses for the compositeness.\n")
                else:
                    print(str(prime) + " is composite and divisible by: " + str(divisors) +
                          ";\n   " + str(witnesses) + " is the witnesses for the compositeness.\n")
            else:
                if test == "1f":
                    print(str(prime) + " is composite, divisors unknown;\n   " +
                          str(witnesses[0]) + " is the witnesses for the compositeness.\n")
                else:
                    print(str(prime) + " is composite, divisors unknown;\n   " +
                          str(witnesses) + " are the witnesses for the compositeness.\n")

    if test == "2" or test == "2f":
        prime = digits(input("what number?: "))

        while prime < 2:
            prime = digits(input("what number?: "))
        
        print("")

        if test == "2f":
            primeness = mil(prime, True)
        else:
            primeness = mil(prime, False)

        if primeness[0] == False:
            print(str(prime) + " is prime\n")
        else:
            if test == "2f":
                print(str(prime) + " is composite and;\n    " +
                      str(primeness[1][0]) + " is the witness of the compositeness\n")
            else:
                if len(primeness[2]) >= 1:
                    print(str(prime) + " is composite and divisible by: " + str(primeness[2]) + ";\n   " + str(
                        primeness[1]) + " are the witnesses for the compositeness.\n")
                else:
                    print(str(prime) + " is composite, divisors unknown;\n   " +
                          str(primeness[1]) + " are the witnesses for the compositeness.\n")

    if test == "3" or test == "3f":
        lowbound = input("count primes from (0): ")
        if lowbound != "":
            lowbound = digits(lowbound)
            if lowbound < 2:
                lowbound = 2
        else:
            lowbound = 2

        upbound = digits(input("count primes up to: "))

        while upbound <= lowbound:
            upbound = digits(input("count primes up to: "))

        pi = 0
        prime = []

        for number in range(lowbound, upbound+1):
            if mil(number, True)[0] == False:
                pi += 1
                if test == "3":
                    prime.append(number)
                    if test == "3":
                        print(".", end="")
                        
        if test == "3":
            print("\n")
        
        print("\n" + str(pi) + " primes between those bounds\n")
        if test == "3":
            print(str(prime) + "\n")

    if test == "4" or test == "4f":
        integer = digits(input("find next prime from: "))
        while integer < 2:
            integer = digits(input("find next prime from: "))
        
        how_many = digits(input("how many primes(1): "))
        if how_many < 1:
            how_many = 1
        prime = []

        while len(prime) < how_many:
            if mil(integer, True)[0] == False:
                prime.append(integer)
            else:
                if test == "4":
                    print(".", end="")
            integer += 1
        

        print("\n")
        print(prime, "", "are the next primes\n")
