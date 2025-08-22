import json
import os
import random
import sys
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, Button, Input, Static
from textual.events import MouseDown, MouseScrollDown, MouseScrollUp, Key, MouseMove, MouseUp
from textual.containers import HorizontalGroup, HorizontalScroll, Center, Container
from textual.widget import Widget
from textual.reactive import reactive, var
from textual.message import Message
from textual.screen import ModalScreen
from rich.text import Text, Span

from data import BLOCKS, Block, get_block
from world import World

class BlockBar(Widget):
    class Selected(Message):
        def __init__(self, block: Block) -> None:
            self.block = block
            super().__init__()

    block = reactive(BLOCKS[0], recompose=True)

    def compose(self):
        btns = []
        for block in BLOCKS:
            block_id, char, color, name = block
            btn = Button(label=f"{char}: {name}", id=block_id, classes=("active" if self.block.id == block_id else ""))
            btn.styles.color = color.split(" ")[0]
            btn.can_focus = False
            btns.append(btn)
        yield HorizontalScroll(*btns)

    def on_button_pressed(self, evt: Button.Pressed):
        self.select_block(get_block(evt.button.id))
    
    def select_block(self, block: Block):
        # self.log.error("  ".join(traceback.format_stack()))
        # self.notify("changed block")
        # for btn in self.query_children(Button).nodes:
        #     if btn.id == block.id: self.focus(btn)
        self.post_message(BlockBar.Selected(block))
    def next_block(self):
        i = BLOCKS.index(self.block)
        self.select_block(BLOCKS[(i + 1) if (i <= len(BLOCKS) - 2) else 0])
    def previous_block(self):
        i = BLOCKS.index(self.block)
        self.select_block(BLOCKS[(i - 1) if i >= 1 else (len(BLOCKS) - 1)])

# was used to limit size and show error, not necessary anymore
OVERSIZED = -1
class WorldDisplay(Static):
    def __init__(self, world: World, start_cam: tuple[int, int], mt: "MineTerminal"):
        super().__init__(markup=False, expand=True, shrink=False)
        self.world = world
        self.world.on_update = self.refresh
        self._drag = False
        self.set_reactive(WorldDisplay.camera, start_cam)
        self.mt = mt

        # if this is set to True it causes enourmous lag -_-
        self.auto_links = False
    
    @property
    def allow_select(self):
        return False

    camera = reactive((0, 0))

    def render(self):
        w, h = self.size
        camx, camy = self.camera
        # cx, cy, cb = (int(v) for v in self.change.split(","))
        # out = f"{cx} - {cy}\n"
        
        out = "Due to performance issues, the render size is limited to 125x40.\n\n" if h == OVERSIZED else ""
        spans = []
        spanoffset = len(out) if h == OVERSIZED else 0
        if h == OVERSIZED: spans.append(Span(0, spanoffset, "#AA0000"))

        tx, ty = 0, 0
        for y in range(camy + h - 1 + (2 if h == OVERSIZED else 0), camy - 1, -1):
            for x in range(camx, camx + w):
                block = self.world.get_block_at(x, y)
                if block:
                    out += block.char # if not (cx == x and cy == y) else "!"
                    spans.append(Span(ty * w + tx + spanoffset, ty * w + tx + spanoffset + 1, block.color))
                else:
                    out += "█"
                    spans.append(Span(ty * w + tx + spanoffset, ty * w + tx + spanoffset + 1, "#87CEFA"))
                tx += 1
            ty += 1
            tx = 0
        return Text(out, spans=spans)

    def on_mouse_down(self, evt: MouseDown):
        # self.change = f"{evt.x + self.camera[0]},{self.size.height - evt.y + self.camera[1] - 1},{evt.button}"
        cx = evt.x + self.camera[0]
        cy = self.size.height - evt.y + self.camera[1] - 1 + (4 if self.size.height == OVERSIZED else 0)
        self.world.set_block_at(cx, cy, self.mt.block if evt.button != 3 else None)
        # if self.size.area < 1500:
        self._drag = True
    def on_mouse_up(self, evt: MouseUp):
        self._drag = False
    
    def on_mouse_move(self, evt: MouseMove):
        if self._drag:
            cx = evt.x + self.camera[0]
            cy = self.size.height - evt.y + self.camera[1] - 1 + (4 if self.size.height == OVERSIZED else 0)
            self.world.set_block_at(cx, cy, self.mt.block if evt.button != 3 else None)


class SetSeedScreen(ModalScreen):
    def __init__(self, seed: int):
        super().__init__()
        self.seed = seed
    def compose(self):
        yield Container(
            Label("[b]Change seed[/]"),
            Label("Warning: all changes to the current world are lost when updating the seed (if you change it).\n"),
            Input(type="integer", placeholder="Seed", value=str(self.seed)),
            HorizontalGroup(
                Button("Save", "warning", id="save"),
                Button("Cancel", id="cancel"),
            ),
        )
    def on_input_changed(self, evt: Input.Changed):
        if evt.input.value != "":
            self.seed = int(evt.input.value)
        else: self.seed = 0
    def on_input_submitted(self, evt: Input.Submitted):
        self.dismiss(self.seed)
    def on_button_pressed(self, evt: Button.Pressed):
        if evt.button.id == "save":
            self.dismiss(self.seed)
        else:
            self.dismiss(None)

class CloseScreen(ModalScreen[bool]):
    def compose(self):
        yield Container(
            Label("[b]Quit and save?[/]"),
            Label("Do you want to save your game and quit?"),
            HorizontalGroup(
                Button("Yes", "primary", id="yes"),
                Button("Don't save", "warning", id="no_save"),
                Button("Cancel", "default", id="cancel"),
            ),
        )
    def on_button_pressed(self, evt: Button.Pressed):
        if evt.button.id == "yes":
            self.dismiss(True)
        elif evt.button.id == "no_save":
            self.app.exit()
        elif evt.button.id == "cancel":
            self.dismiss(False)

class MineTerminal(Widget):
    """A 2D sandbox game for the terminal."""

    block = var(BLOCKS[0])
    camera = var((0, 0))
    playing = var(True)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield WorldDisplay(self.world, self.camera, self)
        yield BlockBar()

    def on_block_bar_selected(self, evt: BlockBar.Selected):
        if not self.playing: return
        self.block = evt.block
        self.focus()
    
    def watch_block(self, val: str):
        if not self.playing: return
        self.query_one(BlockBar).block = val
    
    def watch_camera(self, val: tuple[int, int]):
        if not self.playing: return
        self.query_one(WorldDisplay).camera = val

    def __init__(self, load = True):
        super().__init__()

        data = {}
        if load and os.path.isfile("mineterminal.dat"):
            with open("mineterminal.dat", "r") as f:
                data = json.load(f)
        
        self.world = World(int(data["meta"]["seed"]) if "meta" in data else random.randint(1, int(1e20)))
        for coords in data:
            if coords != "meta":
                cx, cy = (int(v) for v in coords.split(","))
                self.world.changed[(cx, cy)] = get_block(data[coords]) if data[coords] is not None else None
        self.set_reactive(MineTerminal.camera, tuple(data["meta"]["cam"]) if "meta" in data else (0, self.world.default_height_at(0) - 5))
        self.can_focus = True
        self.focus()
    
    def on_mouse_scroll_up(self, evt: MouseScrollUp):
        if not self.playing: return
        self.query_one(BlockBar).previous_block()

    def on_mouse_scroll_down(self, evt: MouseScrollDown):
        if not self.playing: return
        self.query_one(BlockBar).next_block()
    
    def on_key(self, evt: Key):
        if not self.playing: return
        camx, camy = self.camera
        if evt.name in ["right", "d"]: self.camera = (camx + 1, camy)
        elif evt.name in ["left", "a"]: self.camera = (camx - 1, camy)
        elif evt.name in ["up", "w"]: self.camera = (camx, camy + 1)
        elif evt.name in ["down", "s"]: self.camera = (camx, camy - 1)
    
    async def _update_seed(self, val: int):
        self.playing = True
        if val == self.world.seed or val is None: return
        self.world = World(val)
        # when using recompose, the BINDINGS just disappear - so instead, I update everything manually and only recompose the world display
        self.set_reactive(MineTerminal.camera, (0, self.world.default_height_at(0) - 5))
        wd = self.query_one(WorldDisplay)
        wd.world = self.world
        wd.world.on_update = wd.refresh
        wd.set_reactive(WorldDisplay.camera, self.camera)
        wd.refresh()
        self.notify(f"New seed: {val}")
        self.focus()
    def action_set_seed(self):
        self.playing = False
        self.app.push_screen(SetSeedScreen(self.world.seed), callback=self._update_seed)

class MTApp(App):

    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("c", "set_seed", "change seed"),
        Binding("right click", "_", "break", tooltip="Break block mouse is hovering over."),
        Binding("left click", "__", "place", tooltip="Place selected block."),
    ]

    def __init__(self, driver_class = None, css_path = None, watch_css = False, ansi_color = False):
        super().__init__(driver_class, css_path, watch_css, ansi_color)
        self.playing = True
        self.title = "⛏ MineTerminal 2D"
        self.set_reactive(MTApp.welcome, "skip" not in sys.argv)

    welcome = reactive(True, recompose=True)
    load = var(True)

    def compose(self):
        if self.welcome:
            with Center():
                yield Label("[b]Welcome to[/]")
                yield Label(" __  __  _            _______                      _                _\n|  \\/  |(_)          |__   __|                    (_)              | |\n| \\  / | _  _ __    ___ | |  ___  _ __  _ __ ___   _  _ __    __ _ | |\n| |\\/| || || '_ \\  / _ \\| | / _ \\| '__|| '_ ` _ \\ | || '_ \\  / _` || |\n| |  | || || | | ||  __/| ||  __/| |   | | | | | || || | | || (_| || |\n|_|  |_||_||_| |_| \\___||_| \\___||_|   |_| |_| |_||_||_| |_| \\__,_||_|\n")
                yield Label("[i]Camera controls:[/]\n  ⬅ Left\n  ⬆ Up\n  ➡ Right\n  ⬇ Down")
                yield Label("[i]Block controls:[/]\n  ⇕ Scroll to switch blocks (or click the buttons)\n  ◀ (Press or hold) Left click to Place\n  ▶ (Press or hold) Right click to Break\n")
                yield Label("Add \"skip\" after the starting prompt to skip this screen.\n")
                if os.path.isfile("mineterminal.dat"): yield Label("You have save data available! Click \"Load\" to load.\n")
                with HorizontalGroup():
                    if os.path.isfile("mineterminal.dat"):
                        yield Button("Load", "success", id="load")
                        yield Button("Start new", "primary", id="new")
                    else:
                        yield Button("Start", "primary", id="start")
                    yield Button("Quit", "default", id="quit")
        else:
            yield Header()
            yield MineTerminal(self.load)
            yield Footer()
    
    def on_button_pressed(self, evt: Button.Pressed):
        self.welcome = False
        self.load = evt.button.id == "load"
        if evt.button.id == "quit":
            self.app.exit()
    
    def action_set_seed(self):
        self.query_one(MineTerminal).action_set_seed()

    def _close_callback(self, val: bool):
        if val:
            mt = self.query_one(MineTerminal)
            world, cam = mt.world, mt.camera
            data = { "meta": { "seed": world.seed, "cam": cam } }
            for coord in world.changed:
                if world.changed[coord] is not None:
                    data[f"{coord[0]},{coord[1]}"] = world.changed[coord].id
                else:
                    data[f"{coord[0]},{coord[1]}"] = None
            with open("mineterminal.dat", "w") as f:
                json.dump(data, f)
            self.app.exit(len(data))
        else:
            self.playing = True
    async def action_quit(self):
        if not self.playing or self.welcome: self.app.exit()
        self.playing = False
        self.push_screen(CloseScreen(), callback=self._close_callback)


if __name__ == "__main__":
    app = MTApp()
    res = app.run()
    if res: print("Saved", res, "blocks to mineterminal.dat.")
