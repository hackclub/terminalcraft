from textual.app import App, ComposeResult
from textual.widgets import Static, Button, Checkbox, Label
from textual.containers import Vertical, Horizontal
from textual.events import Key
from rich.text import Text
import random

MAP_WIDTH = 30 + 1
MAP_HEIGHT = 20 + 1


class Rock:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

    def move(self):
        self.x += self.dx
        self.y += self.dy


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy, map_width, map_height):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < map_width and 0 <= new_y < map_height:
            self.x = new_x
            self.y = new_y
            return True
        return False


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [['.' for _ in range(width)] for _ in range(height)]
        self.stars = []
        center_x, center_y = width // 2, height // 2
        for _ in range(10):
            while True:
                x = random.randint(0, width - 1)
                y = random.randint(0, height - 1)
                if abs(x - center_x) > 5 or abs(y - center_y) > 5:
                    self.stars.append((x, y))
                    break


class GameWidget(Static):
    def __init__(self, map_width=MAP_WIDTH, map_height=MAP_HEIGHT):
        super().__init__()
        self.game_map = GameMap(map_width, map_height)
        self.player = Player(map_width // 2, map_height // 2)
        self.rocks = []
        self.game_over = False
        self.survival_time = 0
        self.map_width = map_width
        self.map_height = map_height
        self.score = 0

    def spawn_rock(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x, y, dx, dy = random.randint(0, self.map_width - 1), 0, 0, 1
        elif side == 'bottom':
            x, y, dx, dy = random.randint(0, self.map_width - 1), self.map_height - 1, 0, -1
        elif side == 'left':
            x, y, dx, dy = 0, random.randint(0, self.map_height - 1), 1, 0
        else:
            x, y, dx, dy = self.map_width - 1, random.randint(0, self.map_height - 1), -1, 0
        self.rocks.append(Rock(x, y, dx, dy))

    def move_rocks(self):
        for rock in self.rocks:
            rock.move()
        self.rocks = [
            rock for rock in self.rocks
            if 0 <= rock.x < self.map_width and 0 <= rock.y < self.map_height
        ]

    def check_collision(self):
        for rock in self.rocks:
            if rock.x == self.player.x and rock.y == self.player.y:
                self.game_over = True
                return

        player_pos = (self.player.x, self.player.y)
        if player_pos in self.game_map.stars:
            self.game_map.stars.remove(player_pos)
            self.score += 25

    def render(self) -> Text:
        if self.game_over:
            return Text(
                f"\n\nYOU LOSE\n\nSurvival Time: {self.survival_time:.1f} seconds\nScore: {self.score}\n\nPress R to retry or Q to return to the menu.",
                justify="center")

        base_score = int(self.survival_time * 10)
        total_score = base_score + self.score

        minutes = int(self.survival_time // 60)
        seconds = int(self.survival_time % 60)
        time_display = f"Time: {minutes:02d}:{seconds:02d} | Score: {total_score}"

        grid = [[' ' for _ in range(self.map_width)] for _ in range(self.map_height)]

        for x, y in self.game_map.stars:
            if 0 <= x < self.map_width and 0 <= y < self.map_height:
                grid[y][x] = "*"

        for y in range(self.map_height):
            for x in range(self.map_width):
                if x == self.player.x and y == self.player.y:
                    grid[y][x] = "O"
                elif any(rock.x == x and rock.y == y for rock in self.rocks):
                    grid[y][x] = "x"
                elif grid[y][x] == ' ':
                    grid[y][x] = "_"

        display_lines = []
        for row in grid:
            display_lines.append("".join(row))

        return Text(time_display + "\n\n" + "\n".join(display_lines), justify="center")


class MenuWidget(Vertical):
    def compose(self) -> ComposeResult:
        yield Button("Play", id="play")
        yield Button("Options", id="options")
        yield Button("Leave", id="leave")


class OptionsWidget(Vertical):
    def compose(self) -> ComposeResult:
        self.styles.align = ("center", "middle")
        self.styles.content_align = ("center", "middle")
        yield Label("Game Options", id="options-title")

        yield Horizontal(
            Label("Rocks:"),
            Checkbox("More rocks", id="more-rocks", value=False),
            Checkbox("Faster rocks", id="faster-rocks", value=False),
            id="rock-options"
        )

        yield Horizontal(
            Label("Map Size:"),
            Checkbox("Large", id="large-map", value=False),
            id="map-options"
        )

        yield Button("Back to menu", id="back-to-menu")


class GameApp(App):
    CSS_PATH = "styles.tcss"

    def __init__(self):
        super().__init__()
        self.state = "menu"
        self.game_widget = None
        self.menu_widget = None
        self.options_widget = None
        self.rock_timer = None
        self.time_timer = None

        self.settings = {
            "more_rocks": False,
            "faster_rocks": False,
            "large_map": False
        }

    def compose(self) -> ComposeResult:
        if self.state == "menu":
            self.menu_widget = MenuWidget()
            yield self.menu_widget
        elif self.state == "options":
            self.options_widget = OptionsWidget()
            yield self.options_widget
        else:
            self.game_widget = GameWidget()
            yield self.game_widget

    def on_mount(self):
        if self.state == "game":
            self.rock_timer = self.set_interval(0.5, self.update_rocks)
            self.time_timer = self.set_interval(0.5, self.update_time)

    def update_rocks(self):
        if self.game_widget and not self.game_widget.game_over:
            self.game_widget.spawn_rock()
            self.game_widget.move_rocks()
            self.game_widget.check_collision()
            self.game_widget.refresh()

    def update_time(self):
        if self.game_widget and not self.game_widget.game_over:
            self.game_widget.survival_time += 0.5
            self.game_widget.refresh()

    def on_button_pressed(self, event):
        if event.button.id == "play":
            self.state = "game"
            self._clear_widgets()

            map_width = MAP_WIDTH * 2 if self.settings["large_map"] else MAP_WIDTH
            map_height = MAP_HEIGHT * 2 if self.settings["large_map"] else MAP_HEIGHT

            self.game_widget = GameWidget(
                map_width=map_width,
                map_height=map_height
            )

            self.mount(self.game_widget)

            rock_interval = 0.3 if self.settings["faster_rocks"] else 0.5
            self.rock_timer = self.set_interval(rock_interval, self.update_rocks)
            self.time_timer = self.set_interval(0.5, self.update_time)

            if self.settings["more_rocks"]:
                for _ in range(5):
                    self.game_widget.spawn_rock()

        elif event.button.id == "options":
            self.state = "options"
            self._clear_widgets()
            self.options_widget = OptionsWidget()
            self.mount(self.options_widget)
        elif event.button.id == "back-to-menu":
            self.state = "menu"
            self._clear_widgets()
            self.menu_widget = MenuWidget()
            self.mount(self.menu_widget)
        elif event.button.id == "leave":
            self.exit()

    def on_checkbox_changed(self, event):
        checkbox_to_settings = {
            "more-rocks": "more_rocks",
            "faster-rocks": "faster_rocks",
            "large-map": "large_map"
        }

        if event.checkbox.id in checkbox_to_settings:
            setting_key = checkbox_to_settings[event.checkbox.id]
            self.settings[setting_key] = event.value

    def _clear_widgets(self):
        if self.menu_widget:
            self.menu_widget.remove()
            self.menu_widget = None
        if self.game_widget:
            self.game_widget.remove()
            self.game_widget = None
        if self.options_widget:
            self.options_widget.remove()
            self.options_widget = None

    def on_key(self, event: Key) -> None:
        if self.state == "menu" or self.state == "options" or self.game_widget is None:
            return

        if self.game_widget.game_over:
            if event.key.lower() == "q":
                if self.rock_timer:
                    self.rock_timer.stop()
                if self.time_timer:
                    self.time_timer.stop()
                self.state = "menu"
                self._clear_widgets()
                self.menu_widget = MenuWidget()
                self.mount(self.menu_widget)
            if event.key.lower() == "r":
                self._clear_widgets()

                map_width = MAP_WIDTH * 2 if self.settings["large_map"] else MAP_WIDTH
                map_height = MAP_HEIGHT * 2 if self.settings["large_map"] else MAP_HEIGHT

                self.game_widget = GameWidget(
                    map_width=map_width,
                    map_height=map_height
                )

                self.mount(self.game_widget)

                if self.rock_timer:
                    self.rock_timer.stop()
                if self.time_timer:
                    self.time_timer.stop()

                rock_interval = 0.3 if self.settings["faster_rocks"] else 0.5
                self.rock_timer = self.set_interval(rock_interval, self.update_rocks)
                self.time_timer = self.set_interval(0.5, self.update_time)

                if self.settings["more_rocks"]:
                    for _ in range(5):
                        self.game_widget.spawn_rock()
            return

        key = event.key.lower()
        moved = False
        move_amount = 1

        if key == "q":
            self.exit()
            return
        if key == "w":
            moved = self.game_widget.player.move(0, -move_amount, self.game_widget.map_width, self.game_widget.map_height)
        elif key == "s":
            moved = self.game_widget.player.move(0, move_amount, self.game_widget.map_width, self.game_widget.map_height)
        elif key == "a":
            moved = self.game_widget.player.move(-move_amount, 0, self.game_widget.map_width, self.game_widget.map_height)
        elif key == "d":
            moved = self.game_widget.player.move(move_amount, 0, self.game_widget.map_width, self.game_widget.map_height)

        if moved:
            self.game_widget.check_collision()
            self.game_widget.refresh()

def main():
    app = GameApp()
    app.run()

if __name__ == "__main__":
    main()