from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Label
from textual.containers import Vertical, Horizontal
from pytubefix import YouTube
from moviepy import *
import os

class MyApp(App):
    CSS = """
    #post_submit > Horizontal {
        height: auto;
    }
    """

    youtube_link = None
    download_type = None
    video_quality = None
    audio_quality = None

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Paste YouTube video link here...", id="input_link")
        yield Button("Enter", id="btn_link")
        with Vertical(id="post_submit"):
            pass

    @on(Button.Pressed, "#btn_link")
    @on(Input.Submitted, "#input_link")
    async def accept_input(self):
        input_link = self.query_one("#input_link", Input)
        btn_link = self.query_one("#btn_link", Button)
        link = input_link.value.strip()
        if not link:
            return
        self.youtube_link = link

        input_link.value = ""
        input_link.disabled = True
        btn_link.disabled = True
        self.refresh()

        post = self.query_one("#post_submit", Vertical)
        horizontal = Horizontal()
        await post.mount(horizontal)
        await self.mount(Label(f"Link \"{link}\" submitted", id="summary"))
        await self.mount(Label("Select the type of the file that you want to download"))
        await horizontal.mount(
            Button("Video", id="btn_video"),
            Button("Audio", id="btn_audio"),
        )
        self.refresh()

    @on(Button.Pressed, "#btn_video")
    async def download_video(self):
        self.download_type = "video"
        await self.mount(Label("Video Selected"))
        btn_audio = self.query_one("#btn_audio", Button)
        btn_video = self.query_one("#btn_video", Button)
        btn_audio.disabled = True
        btn_video.disabled = True

        post = self.query_one("#post_submit", Vertical)
        horizontal = Horizontal()
        await post.mount(horizontal)
        await self.mount(Label("Select video quality"))
        await horizontal.mount(
            Button("144p", id="btn_144p", classes="quality-button"),
            Button("240p", id="btn_240p", classes="quality-button"),
            Button("360p", id="btn_360p", classes="quality-button"),
            Button("480p", id="btn_480p", classes="quality-button"),
            Button("720p (HD)", id="btn_720p", classes="quality-button"),
            Button("1080p (Full HD)", id="btn_1080p", classes="quality-button"),
            Button("1440p (2K)", id="btn_1440p", classes="quality-button"),
            Button("2160p (4K)", id="btn_2160p", classes="quality-button")
        )
        self.refresh()

    @on(Button.Pressed, ".quality-button")
    async def select_quality(self, event):
        btn = event.button
        res = btn.id.removeprefix("btn_")
        self.video_quality = res
        await self.mount(Label(f"{res} quality video selected"))

        for btn in self.query(".quality-button").results(Button):
            btn.disabled = True

        post = self.query_one("#post_submit", Vertical)
        horizontal = Horizontal()
        await post.mount(horizontal)
        await self.mount(Label("Are you sure you want to download this video file?"))
        await self.mount(Label("It may take up to 30 minutes depending on the size of the video and your internet speed..."))
        await self.mount(Label("And the program will freeze until the download is complete ❄"))
        await horizontal.mount(
            Button("Yes", id="btn_yes"),
            Button("No", id="btn_no")
        )
        self.refresh()

    @on(Button.Pressed, "#btn_audio")
    async def download_audio(self):
        self.download_type = "audio"
        await self.mount(Label("Audio Selected"))
        btn_audio = self.query_one("#btn_audio", Button)
        btn_video = self.query_one("#btn_video", Button)
        btn_audio.disabled = True
        btn_video.disabled = True

        post = self.query_one("#post_submit", Vertical)
        horizontal = Horizontal()
        await post.mount(horizontal)
        await self.mount(Label("Select audio quality"))
        await horizontal.mount(
            Button("High Quality", id="btn_h_quality"),
            Button("Low Quality", id="btn_l_quality")
        )
        self.refresh()

    @on(Button.Pressed, "#btn_h_quality")
    async def select_high_quality(self):
        self.audio_quality = "high"
        await self.mount(Label("High quality audio selected"))
        btn_h_quality = self.query_one("#btn_h_quality", Button)
        btn_l_quality = self.query_one("#btn_l_quality", Button)
        btn_h_quality.disabled = True
        btn_l_quality.disabled = True

        post = self.query_one("#post_submit", Vertical)
        horizontal = Horizontal()
        await post.mount(horizontal)
        await self.mount(Label("Are you sure you want to download this audio file?"))
        await self.mount(Label("It may take up to 30 minutes depending on the size of the audio and your internet speed..."))
        await self.mount(Label("And the program will freeze until the download is complete ❄"))
        await horizontal.mount(
            Button("Yes", id="btn_yes"),
            Button("No", id="btn_no")
        )
        self.refresh()

    @on(Button.Pressed, "#btn_l_quality")
    async def select_low_quality(self):
        self.audio_quality = "low"
        await self.mount(Label("Low quality audio selected"))
        btn_h_quality = self.query_one("#btn_h_quality", Button)
        btn_l_quality = self.query_one("#btn_l_quality", Button)
        btn_h_quality.disabled = True
        btn_l_quality.disabled = True

        post = self.query_one("#post_submit", Vertical)
        horizontal = Horizontal()
        await post.mount(horizontal)
        await self.mount(Label("Are you sure you want to download this audio file?"))
        await self.mount(Label("It may take up to 30 minutes depending on the size of the audio and your internet speed..."))
        await self.mount(Label("And the program will freeze until the download is complete ❄"))
        await horizontal.mount(
            Button("Yes", id="btn_yes"),
            Button("No", id="btn_no")
        )
        self.refresh()

    @on(Button.Pressed, "#btn_yes")
    async def start_download(self):
        btn_yes = self.query_one("#btn_yes", Button)
        btn_no = self.query_one("#btn_no", Button)
        btn_yes.disabled = True
        btn_no.disabled = True
        self.refresh()
        try:
            yt = YouTube(self.youtube_link)
            title = yt.title.translate({ord(i): None for i in '/\\:*?\"<>|'})
            if self.download_type == "video":
                if self.video_quality == "360p":
                    stream = yt.streams.filter(res=self.video_quality, file_extension="mp4", progressive=True).order_by("resolution").desc().first()
                    stream.download(filename=f"YVD {title}.mp4")
                else:
                    stream = yt.streams.filter(res=self.video_quality, file_extension="mp4", progressive=False).order_by("resolution").desc().first()
                    pre = "audio_"
                    stream.download()
                    yt.streams.filter(type="audio", file_extension="mp4").order_by("abr").desc().first().download(filename_prefix=pre)
                    video = VideoFileClip(f"{title}.{"mp4"}")
                    audio = AudioFileClip(f"{pre}{title}.m4a")
                    final_video = video.with_audio(audio)
                    final_video.write_videofile(f"YVD {title}.{"mp4"}")
                    os.remove(f"{title}.{"mp4"}")
                    os.remove(f"{pre}{title}.m4a")
            else:
                if self.audio_quality == "high":
                    stream = yt.streams.filter(type="audio", file_extension="webm").order_by("abr").desc().first()
                    stream.download()
                    audio = AudioFileClip(f"{title}.m4a")
                    audio.write_audiofile(f"YVD {title}.wav")
                    os.remove(f"{title}.m4a")
                else:
                    stream = yt.streams.filter(type="audio", file_extension="mp4").order_by("abr").first()
                    stream.download()
                    audio = AudioFileClip(f"{title}.m4a")
                    audio.write_audiofile(f"YVD {title}.mp3")
                    os.remove(f"{title}.m4a")

            await self.mount(Label("Your file is ready!"))
        except:
            await self.mount(Label("Sorry the video isn't available with these requirements😥"))
        self.refresh()


    @on(Button.Pressed, "#btn_no")
    async def exit_program(self):
        self.exit()


if __name__ == "__main__":
    MyApp().run()
