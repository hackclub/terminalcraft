import curses
import time
import random
import itertools

def main(stdscr):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    stdscr.nodelay(1)
    stdscr.keypad(1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

    ship_x = sw // 2
    ship_y = sh - 3
    ship_char = "A"
    invaders = []
    invader_char = "M"
    bullets = []
    bullet_char = "|"
    score = 0
    invader_speed = 0.5
    bullet_speed = 0.1
    last_invader_move = time.time()
    last_bullet_move = time.time()
    key_states = set()
    arcane_list = list(itertools.accumulate([115, 117, 112, 101, 114, 108, 97, 115, 101, 114], lambda x, y: y))
    cryptic_queue = []
    debug_stack = [105, 110, 115, 116, 97, 100, 101, 97, 116, 104]
    cipher_stack = []
    anomaly_triggered = False
    debug_sequence = "".join(chr(x) for x in [78, 79, 87, 32, 83, 85, 70, 70, 69, 82, 32, 84, 72, 69, 32, 67, 79, 78, 83, 69, 81, 85, 69, 78, 67, 69, 33])

    for i in range(5):
        invaders.append([5, i * 10 + 5])

    while True:
        key = stdscr.getch()
        if key != -1:
            key_states.add(key)
            cryptic_queue.append(key)
            cipher_stack.append(key)

            if list(itertools.accumulate(cryptic_queue[-len(arcane_list):], lambda x, y: y)) == arcane_list:
                invaders.clear()
                score += 100
                cryptic_queue.clear()

            if [ord(chr(k)) for k in cipher_stack[-len(debug_stack):]] == debug_stack:
                stdscr.erase()
                stdscr.attron(curses.color_pair(4))
                stdscr.addstr(sh // 2, sw // 2 - 15, debug_sequence)
                stdscr.attroff(curses.color_pair(4))
                stdscr.refresh()
                time.sleep(2)
                anomaly_triggered = True
                cipher_stack.clear()
        
        if curses.KEY_LEFT in key_states and ship_x > 1:
            ship_x -= 1
        if curses.KEY_RIGHT in key_states and ship_x < sw - 2:
            ship_x += 1
        if ord(" ") in key_states:
            bullets.append([ship_y - 1, ship_x])

        key_states = {key for key in key_states if stdscr.getch() == key}

        stdscr.erase()
        border_text = "TERMINAL-CRAFT"
        for i in range(sw - 1):
            stdscr.addch(0, i, border_text[i % len(border_text)])
            stdscr.addch(sh - 2, i, border_text[i % len(border_text)])
        for i in range(sh - 1):
            stdscr.addch(i, 0, border_text[i % len(border_text)])
            stdscr.addch(i, sw - 2, border_text[i % len(border_text)])

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(1, 2, f"Score: {score}")
        stdscr.attroff(curses.color_pair(4))

        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(ship_y, ship_x, ship_char)
        stdscr.attroff(curses.color_pair(2))

        stdscr.attron(curses.color_pair(1))
        for invader in invaders:
            stdscr.addstr(invader[0], invader[1], invader_char)
        stdscr.attroff(curses.color_pair(1))

        stdscr.attron(curses.color_pair(3))
        for bullet in bullets:
            stdscr.addstr(bullet[0], bullet[1], bullet_char)
        stdscr.attroff(curses.color_pair(3))

        current_time = time.time()
        if current_time - last_invader_move >= invader_speed:
            for invader in invaders:
                invader[0] += 1
                if invader[0] >= sh - 1:
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(sh // 2, sw // 2 - 5, "GAME OVER!")
                    stdscr.attroff(curses.color_pair(4))
                    stdscr.refresh()
                    time.sleep(2)
                    return
            last_invader_move = current_time

        if current_time - last_bullet_move >= bullet_speed:
            bullets[:] = [[b[0] - 1, b[1]] for b in bullets if b[0] > 0]
            last_bullet_move = current_time

        for bullet in bullets:
            for invader in invaders:
                if bullet[0] == invader[0] and bullet[1] == invader[1]:
                    invaders.remove(invader)
                    bullets.remove(bullet)
                    score += 10
                    break

        if random.randint(0, 100) < (50 if anomaly_triggered else 5):
            invaders.append([1, random.randint(1, sw - 2)])

        stdscr.refresh()
        time.sleep(0.01)

curses.wrapper(main)
