"""program written by e^pi*i+1=0 i.e. Jakub"""

import random as rnd
import math
import argparse as arg
import curses as cs

parser = arg.ArgumentParser(description="Miller-Rabin primality test implementation in Python.")

parser.add_argument("type", help="specifies type of test; use 0 to manualy test a base; use 1 to randomly test a bunch of bases; use 2 to make \
a deterministic test, assuming that extended riemann hypothesis is true or for numbers less than 3317044064679887385961980, its true without this hypothesis;\
 use 3 to calculate pi(x)-pi(y) (its inclusive with those bounds); use 4 to find next primes from a given number; use 5 for art")

parser.add_argument("-f", "--fast", action="store_true", help="use fast mode, which will not print intermediate results,\
                    on example it will not list primes counted in 3rd mode, it will not show progress, and it will stop when any witness is found")

test0 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]

BLOCK_CHAR = "█"
BORDER_CHAR = "│"
TOP_BOTTOM_BORDER_CHAR = "─"
CORNER_CHAR = "┌┐└┘"

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

def check_size(stdscr, changebox = 0):
    global height, width
    size = stdscr.getmaxyx()
    height, width = size[0]-1, 2*(size[1]//2)-2

def draw_box(stdscr, box_height, box_width):
    stdscr.addch(0, 0, CORNER_CHAR[0])
    for x in range(1, box_width):
        stdscr.addch(0, x, TOP_BOTTOM_BORDER_CHAR)
    stdscr.addch(0, box_width, CORNER_CHAR[1])
    for y in range(1, box_height):
        stdscr.addch(y, 0, BORDER_CHAR)
        stdscr.addch(y, box_width, BORDER_CHAR)
    stdscr.addch(box_height, 0, CORNER_CHAR[2])
    for x in range(1, box_width):
        stdscr.addch(box_height, x, TOP_BOTTOM_BORDER_CHAR)
    stdscr.addch(box_height, box_width, CORNER_CHAR[3])


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
    
    if test == "5" or test == "5f":
        start_pos = digits(input("Look at primes after this number, it is possible to scroll later (2): "))
        if start_pos < 2 or start_pos == None:
            start_pos = 2
        
        def main(stdscr):
            cs.curs_set(0)  # Hide cursor
            stdscr.nodelay(1)
            stdscr.timeout(1000)
            stdscr.clear()
            global start_pos
            start = start_pos
            change = 0
            pos = [1, 1]
            global height, width
            
            cs.start_color()
            cs.init_pair(1, cs.COLOR_WHITE, cs.COLOR_BLACK)
            cs.init_pair(2, cs.COLOR_GREEN, cs.COLOR_BLACK)
            stdscr.bkgd(' ', cs.color_pair(1) | cs.A_BOLD)
            
            
            check_size(stdscr)
            primes = [i for i in range(start, start + (3*height)*(width-1)) if mil(i, True)[0] == False]

            while True:
                stdscr.clear()
                prime_count = 0
                check_size(stdscr)
                width_2 = width - change
                draw_box(stdscr, height, width_2)
                stdscr.addstr(height, 1, "'q' - quit, 'j'/'k' - change width, PGUP/PGDN - scroll, arrows - cursor", cs.color_pair(1))
                
                
                stdscr.addstr(pos[0], pos[1], "+", cs.color_pair(2))
                
                for n in primes:
                    if 1+(n - start)//(width_2-1) <= height-1:
                        p_pos = (1+(n - start)//(width_2-1), 1+(n - start)%(width_2-1))
                        
                        if pos[0] == p_pos[0] and pos[1] == p_pos[1]:
                            stdscr.addstr(p_pos[0], p_pos[1], BLOCK_CHAR, cs.color_pair(2))
                        else:
                            stdscr.addstr(p_pos[0], p_pos[1], BLOCK_CHAR, cs.color_pair(1))
                        
                        prime_count += 1
                    
                        
                if change > 17+len(str(start))+len(str(start + (width_2-2)*(height-2))):
                    stdscr.addstr(1, width_2+2, f"Cursor on: {(pos[0]-1)*(width_2-1) + pos[1] - 1 + start}")
                    stdscr.addstr(2, width_2+2, f"Primes on screen: {prime_count}")
                    stdscr.addstr(3, width_2+2, f"Showing from {start} to {start-1 + (width_2-1)*(height-1)}")
                
                
                key = stdscr.getch()
                if key == ord('q'):
                    break
                elif key == ord('k') or key == ord('j'):
                    change += 1 if key == ord('j') else -1
                    if key == ord('j') and pos[1] > width_2 - 3:
                        pos[1] -= 1
                    if change < 0:
                        change = 0
                    elif change > width - 3:
                        change = width - 3
                elif key == cs.KEY_UP or key == cs.KEY_DOWN:
                    pos[0] += 1 if key == cs.KEY_DOWN else -1
                elif key == cs.KEY_LEFT or key == cs.KEY_RIGHT:
                    pos[1] += 1 if key == cs.KEY_RIGHT else -1
                elif key == cs.KEY_PPAGE or key == cs.KEY_NPAGE:
                    start += (height-1) if key == cs.KEY_NPAGE else -(height-1)
                    if start < 2:
                        start = 2
                    primes = [i for i in range(start, start + (6*height)*(width-1)) if mil(i, True)[0] == False]
                
                if pos[0] < 1:
                    pos[0] = 1
                elif pos[0] > height - 1:
                    pos[0] = height - 1
                
                if pos[1] < 1:
                    pos[1] = 1
                elif pos[1] > width_2-1:
                    pos[1] = width_2-1
                stdscr.refresh()
        
        try:
            cs.wrapper(main)
        except cs.error:
            print("Terminal size is too small, please resize it to at least 70 characters wide.")
        break
