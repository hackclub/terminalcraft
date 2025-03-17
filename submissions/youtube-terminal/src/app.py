# youtube-terminal
# ooflet 2025

import sys
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import ContentSwitcher, Footer, Header, Label, Input, Button, LoadingIndicator

from widgets import VideoResult, VideoPlayer, SuggestedVideoResult
from utils.api import search_youtube, get_stream_url, get_video_info

class MainApplication(App):
    """The main application"""

    CSS_PATH = "css/app.tcss"

    def compose(self) -> ComposeResult:
        with Container(id="app"):
            yield Input(placeholder="Search...")
            with ContentSwitcher(initial="home"):
                with VerticalScroll(id="home"):
                    yield Label("Search something up...", classes="centered-text")
                yield VerticalScroll(id="search")
                with Container(id="player"):
                    yield VerticalScroll(id="video-pane")
                    yield VerticalScroll(id="suggestions-pane")

    def on_mount(self):
        self.player = None
        self.title = "Youtube-Terminal"

    def _on_exit_app(self):
        self.play_thread.join(0)
        sys.exit(0) # Force quit everything (very hacky!!!)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.has_class("video-result") or event.button.has_class("suggested-video-result"):
            if self.player != None:
                self.player.playing = False
                self.query_one("#video-pane", VerticalScroll).remove_children()
                self.player = None

            self.query_one(ContentSwitcher).current = "player"
            video_pane = self.query_one("#video-pane", VerticalScroll)

            suggestions_list = self.query_one("#suggestions-pane", VerticalScroll)

            suggestions_list.remove_children()

            indicator = LoadingIndicator()
            suggestions_list.mount(indicator)

            # Make video player
            self.player = VideoPlayer()
            self.play_thread = threading.Thread(target=lambda: self.player.play(get_stream_url(event.button.url)))
            video_pane.mount(self.player)
            self.play_thread.start()

            video_info = await get_video_info(event.button.url)

            title_text = video_info.get("title")

            # textual uses square brackets for markup, replace with regular brackets
            if "[" in title_text:
                title_text = title_text.replace("[", "(")
                title_text = title_text.replace("]", ")")

            self.playback_button = Button("Pause", classes="playback-button")
            video_pane.mount(self.playback_button)
            
            title = Label(title_text)
            details = Label(video_info.get('channel'), classes="details")
            
            video_pane.mount(title)
            video_pane.mount(details)

            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as pool:
                videos = await loop.run_in_executor(pool, search_youtube, title_text)

            indicator.remove()

            for title, details, url, thumbnail_url in videos:
                suggestions_list.mount(SuggestedVideoResult(thumbnail_url, title, details, url))

        if event.button.has_class("playback-button"):
            if self.player.media_player.get_pause():
                self.player.media_player.set_pause(False)
                self.playback_button.label = "Pause"
            else:
                self.player.media_player.set_pause(True)
                self.playback_button.label = "Play"


    @on(Input.Submitted)
    async def search(self):
        input = self.query_one(Input)
        search = input.value

        if search == "":
            return
        
        result_list = self.query_one("#search", VerticalScroll)
        result_list.remove_children()
        
        if self.player != None:
            self.player.playing = False
            self.player.media_player.set_pause(True)
            self.query_one("#video-pane", VerticalScroll).remove_children()
            self.player = None
        
        if search == "something":
            result_list.mount(Label("very smart of you haha"))

        switcher = self.query_one(ContentSwitcher)
        switcher.current = "search"
        
        indicator = LoadingIndicator()
        result_list.mount(indicator)

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            videos = await loop.run_in_executor(pool, search_youtube, search)

        indicator.remove()

        for title, details, url, thumbnail_url in videos:
            result_list.mount(VideoResult(thumbnail_url, title, details, url))


    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

MainApplication().run()