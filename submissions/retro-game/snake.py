import curses
import random


def main(stdscr):
    curses.curs_set(0)
    stdscr.timeout(150)
    stdscr.keypad(True)

    try:
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        use_colors = True
    except:
        use_colors = False

    max_y, max_x = stdscr.getmaxyx()

    height = max_y - 4
    width = max_x - 4

    game_win = curses.newwin(height + 2, width + 2, 1, 1)
    game_win.keypad(True)
    game_win.timeout(150)

    stdscr.clear()
    welcome_msg = "SNAKE GAME - Press any key to start"
    stdscr.addstr(max_y // 2, (max_x - len(welcome_msg)) // 2, welcome_msg)
    stdscr.refresh()
    stdscr.getch()

    snake = [
        [height // 2, width // 2],
        [height // 2, width // 2 - 1],
        [height // 2, width // 2 - 2],
    ]

    food = [height // 2, width // 2 + 5]

    special_food = None
    special_food_timer = 0

    direction = curses.KEY_RIGHT

    score = 0

    while True:
        game_win.clear()
        game_win.box()

        stdscr.addstr(
            0, 2, f"Score: {score}   ", curses.color_pair(4) if use_colors else 0
        )
        stdscr.refresh()

        for i, segment in enumerate(snake):
            y, x = segment
            if i == 0:
                game_win.addstr(y, x, "O", curses.color_pair(1) if use_colors else 0)
            else:
                game_win.addstr(y, x, "o", curses.color_pair(1) if use_colors else 0)

        if food:
            game_win.addstr(
                food[0], food[1], "*", curses.color_pair(2) if use_colors else 0
            )

        if special_food:
            game_win.addstr(
                special_food[0],
                special_food[1],
                "$",
                curses.color_pair(5) if use_colors else 0,
            )

        game_win.refresh()

        key = stdscr.getch()

        if key == ord("q"):
            break

        if key == ord("p"):
            game_win.addstr(
                height // 2,
                width // 2 - 10,
                "PAUSED - Press 'p' to resume",
                curses.color_pair(4) if use_colors else 0,
            )
            game_win.refresh()

            stdscr.timeout(-1)
            while True:
                ch = stdscr.getch()
                if ch == ord("p"):
                    break
                elif ch == ord("q"):
                    return

            stdscr.timeout(150)

        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            if (
                (direction == curses.KEY_DOWN and key != curses.KEY_UP)
                or (direction == curses.KEY_UP and key != curses.KEY_DOWN)
                or (direction == curses.KEY_LEFT and key != curses.KEY_RIGHT)
                or (direction == curses.KEY_RIGHT and key != curses.KEY_LEFT)
            ):
                direction = key

        head = snake[0].copy()
        if direction == curses.KEY_DOWN:
            head[0] += 1
        elif direction == curses.KEY_UP:
            head[0] -= 1
        elif direction == curses.KEY_LEFT:
            head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            head[1] += 1

        if (
            head[0] <= 0
            or head[0] >= height + 1
            or head[1] <= 0
            or head[1] >= width + 1
        ):
            break

        if head in snake:
            break

        snake.insert(0, head)

        if head == food:
            score += 10

            for _ in range(100):
                food = [random.randint(1, height), random.randint(1, width)]
                if food not in snake and (not special_food or food != special_food):
                    break

            if special_food is None and random.random() < 0.1:
                for _ in range(100):
                    special_food = [random.randint(1, height), random.randint(1, width)]
                    if special_food not in snake and special_food != food:
                        break
                special_food_timer = 50

        elif special_food and head == special_food:
            score += 50

            special_food = None
            special_food_timer = 0
        else:
            snake.pop()

        if special_food:
            special_food_timer -= 1
            if special_food_timer <= 0:
                special_food = None

    stdscr.clear()
    game_over_msg = f"Game Over! Final Score: {score}"
    stdscr.addstr(
        max_y // 2,
        (max_x - len(game_over_msg)) // 2,
        game_over_msg,
        curses.color_pair(2) if use_colors else 0,
    )
    stdscr.addstr(max_y // 2 + 2, (max_x - 22) // 2, "Press any key to exit")
    stdscr.refresh()
    stdscr.timeout(-1)
    stdscr.getch()


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        print(f"An error occurred: {e}")
