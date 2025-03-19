import curses
from random import randint, choice
from time import time

def main(stdscr):
    
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(75)  

    
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)     
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)    
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) 
    
    for y in range(sh):
        try:
            w.addch(y, 0, curses.ACS_VLINE, curses.color_pair(2))
            w.addch(y, sw - 1, curses.ACS_VLINE, curses.color_pair(2))
        except curses.error:
            pass
    for x in range(sw):
        try:
            w.addch(0, x, curses.ACS_HLINE, curses.color_pair(2))
            w.addch(sh - 1, x, curses.ACS_HLINE, curses.color_pair(2))
        except curses.error:
            pass

    
    snk_x = sw // 4
    snk_y = sh // 2
    snake = [
        [snk_y, snk_x],
        [snk_y, snk_x - 1],
        [snk_y, snk_x - 2]
    ]
    
    
    food_types = [
        (curses.ACS_PI, 3, 1),       
        (curses.ACS_DIAMOND, 4, 3),  
        (curses.ACS_STERLING, 5, 5)  
    ]
    
    
    food_type = choice(food_types)
    food = [sh // 2, sw // 2]
    food_char, food_color, food_points = food_type
    w.addch(food[0], food[1], food_char, curses.color_pair(food_color))

    
    key = curses.KEY_RIGHT
    score = 0
    paused = False
    last_food_time = time()
    bonus_food_active = False
    bonus_food = None

    
    high_score = load_high_score()

    
    try:
        score_str = f"Score: {score} | High Score: {high_score}"
        w.addstr(2, sw // 2 - len(score_str) // 2, score_str)
    except curses.error:
        pass

    while True:
        
        next_key = w.getch()
        
        
        if next_key == ord(' '):
            paused = not paused
            if paused:
                try:
                    w.addstr(sh // 2, sw // 2 - 3, "PAUSED")
                    w.refresh()
                except curses.error:
                    pass
            else:
                
                try:
                    w.addstr(sh // 2, sw // 2 - 3, "      ")
                except curses.error:
                    pass
        
        
        if paused:
            continue
            
        key = key if next_key == -1 else next_key

        
        if key == curses.KEY_DOWN and snake[0][0] + 1 != snake[1][0]:
            new_head = [snake[0][0] + 1, snake[0][1]]
        elif key == curses.KEY_UP and snake[0][0] - 1 != snake[1][0]:
            new_head = [snake[0][0] - 1, snake[0][1]]
        elif key == curses.KEY_LEFT and snake[0][1] - 1 != snake[1][1]:
            new_head = [snake[0][0], snake[0][1] - 1]
        elif key == curses.KEY_RIGHT and snake[0][1] + 1 != snake[1][1]:
            new_head = [snake[0][0], snake[0][1] + 1]
        else:
            
            if key == curses.KEY_DOWN:
                new_head = [snake[0][0] + 1, snake[0][1]]
            elif key == curses.KEY_UP:
                new_head = [snake[0][0] - 1, snake[0][1]]
            elif key == curses.KEY_LEFT:
                new_head = [snake[0][0], snake[0][1] - 1]
            elif key == curses.KEY_RIGHT:
                new_head = [snake[0][0], snake[0][1] + 1]

        
        snake.insert(0, new_head)
        
        
        if snake[0][0] in [0, sh - 1] or snake[0][1] in [0, sw - 1] or snake[0] in snake[1:]:
            
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            
            w.clear()
            try:
                w.addstr(sh // 2 - 2, sw // 2 - len("Game Over") // 2, "Game Over")
                w.addstr(sh // 2, sw // 2 - len(f"Final Score: {score}") // 2, f"Final Score: {score}")
                w.addstr(sh // 2 + 2, sw // 2 - len(f"High Score: {high_score}") // 2, f"High Score: {high_score}")
            except curses.error:
                pass
            w.refresh()
            curses.napms(3000)
            break

        
        if snake[0] == food:
            score += food_points
            
            
            if score % 10 == 0 and w.timeout() > 40:
                w.timeout(w.timeout() - 5)  
                
            
            food = None
            food_type = choice(food_types)
            food_char, food_color, food_points = food_type
            
            
            attempts = 0
            while food is None and attempts < 20:
                nf = [
                    randint(1, sh - 2),
                    randint(1, sw - 2)
                ]
                food = nf if nf not in snake else None
                attempts += 1
                
            if food:
                try:
                    w.addch(food[0], food[1], food_char, curses.color_pair(food_color))
                except curses.error:
                    pass
                    
            
            if randint(1, 10) == 1 and not bonus_food_active:
                bonus_food_active = True
                last_food_time = time()
                bonus_food = None
                
                
                while bonus_food is None:
                    bf = [
                        randint(1, sh - 2),
                        randint(1, sw - 2)
                    ]
                    if bf not in snake and bf != food:
                        bonus_food = bf
                
                try:
                    w.addch(bonus_food[0], bonus_food[1], '$', curses.A_BOLD | curses.color_pair(5))
                except curses.error:
                    pass
        else:
            tail = snake.pop()
            try:
                w.addch(tail[0], tail[1], ' ')
            except curses.error:
                pass

        
        if bonus_food_active:
            
            if snake[0] == bonus_food:
                score += 10  
                bonus_food_active = False
                bonus_food = None
            
            elif time() - last_food_time > 10:
                try:
                    w.addch(bonus_food[0], bonus_food[1], ' ')
                except curses.error:
                    pass
                bonus_food_active = False
                bonus_food = None
                
        
        for i, segment in enumerate(snake):
            try:
                
                if i == 0:
                    w.addch(segment[0], segment[1], curses.ACS_CKBOARD, curses.A_BOLD | curses.color_pair(1))
                else:
                    w.addch(segment[0], segment[1], curses.ACS_CKBOARD, curses.color_pair(1))
            except curses.error:
                pass

        
        for y in range(sh):
            try:
                w.addch(y, 0, curses.ACS_VLINE, curses.color_pair(2))
                w.addch(y, sw - 1, curses.ACS_VLINE, curses.color_pair(2))
            except curses.error:
                pass
        for x in range(sw):
            try:
                w.addch(0, x, curses.ACS_HLINE, curses.color_pair(2))
                w.addch(sh - 1, x, curses.ACS_HLINE, curses.color_pair(2))
            except curses.error:
                pass
                
        
        try:
            score_str = f"Score: {score} | High Score: {high_score}"
            w.addstr(2, sw // 2 - len(score_str) // 2, score_str)
        except curses.error:
            pass
        
        w.refresh()
        

def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return 0
    except ValueError:
        return 0

def save_high_score(high_score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(high_score))
    except Exception as e:
        print(f"Error saving high score: {e}")

if __name__ == "__main__":
    curses.wrapper(main)
