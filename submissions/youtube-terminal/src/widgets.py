import asyncio
import time
import httpx
import numpy
from io import BytesIO
from PIL import Image
from rich.console import Console
from rich_pixels import Pixels
from textual import on
from textual.containers import Container
from textual.widgets import Static, Label, Button, LoadingIndicator

import threading

from PIL import Image
from rich_pixels import Pixels
from ffpyplayer.player import MediaPlayer


class VideoResult(Container, Button):
    def __init__(self, thumbnail_url: str, title: str, details: str, url: str):
        super().__init__()
        self.url = url
        self.classes = "video-result"
        self.thumbnail_url = thumbnail_url
        if "[" in title:
            title = title.replace("[", "(")
            title = title.replace("]", ")")
        self.title = title
        self.details = details
        self.label = ""
        self.thumbnail_pixels = "Loading..."

    async def fetch_thumbnail(self):
        if not self.thumbnail_url.startswith("http"):
            return
        async with httpx.AsyncClient() as client:
            response = await client.get(self.thumbnail_url, timeout=5)  # Set timeout
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content)).convert("RGB").resize((35, 20))
                self.thumbnail_pixels = Pixels.from_image(image)
                self.refresh()


    async def _on_mount(self):
        self.mount(Label(self.title, classes="video-title"))
        self.mount(Label(self.details, classes="details"))
        await self.fetch_thumbnail()
        self.mount(Static(self.thumbnail_pixels, classes="thumbnail"))

class SuggestedVideoResult(Container, Button):
    def __init__(self, thumbnail_url: str, title: str, details: str, url: str):
        super().__init__()
        self.url = url
        self.classes = "suggested-video-result"
        self.thumbnail_url = thumbnail_url
        if "[" in title:
            title = title.replace("[", "(")
            title = title.replace("]", ")")
        self.title = title
        self.details = details
        self.label = ""
        self.thumbnail_pixels = "Loading..."

    async def fetch_thumbnail(self):
        if not self.thumbnail_url.startswith("http"):
            return
        async with httpx.AsyncClient() as client:
            response = await client.get(self.thumbnail_url, timeout=5)  # Set timeout
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content)).convert("RGB").resize((35, 20))
                self.thumbnail_pixels = Pixels.from_image(image)
                self.refresh()

    async def _on_mount(self):
        await self.fetch_thumbnail()
        self.mount(Static(self.thumbnail_pixels, classes="suggested-thumbnail"))
        self.mount(Label(self.title, classes="video-title"))
        self.mount(Label(self.details, classes="details"))

class VideoPlayer(Container):
    def __init__(self):
        super().__init__()
        self.loading_widget = LoadingIndicator()
        self.static = Static()
        self.static.classes = "video-player-static"
        self.classes = "video-player"
        self.video_url = None
        self.playing = True  # Track playback state
        self.media_player = None

        self.prev_frame = ""

        self.loading_widget.visible = True
        self.static.visible = False

    async def on_mount(self):
        self.mount(self.static)
        self.mount(self.loading_widget)

    def play(self, video_url: str):
        self.media_player = MediaPlayer(video_url, autoexit=True)

        self.loading_widget.visible = False
        self.static.visible = True

        try:
            while self.playing:
                frame, val = self.media_player.get_frame()

                if val == 'eof' and not self.media_player.get_pause():
                    break
                elif frame is None:
                    continue
                else:
                    img, timestamp = frame
                    w, h = img.get_size()

                    # Convert frame to numpy array
                    frame_data = img.to_bytearray()
                    array = numpy.frombuffer(frame_data[0], dtype=numpy.uint8).reshape(h, w, 3)

                    # Convert to Pillow image
                    image = Image.fromarray(array, "RGB")
                    image.thumbnail((100, 100))
                    
                    pixels = Pixels.from_image(image)

                    if self.prev_frame != pixels:
                        self.prev_frame = pixels
                        self.app.call_from_thread(self.static.update, pixels)

                    current_frame, timestamp = self.media_player.get_frame()
                    time.sleep(timestamp)

        finally:
            self.app.call_from_thread(self.static.update, "closed")
            self.media_player.close()