import asyncio
import yt_dlp

def shorten_views(views):
    if views == None:
        return "??? views"
    
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B".rstrip("0").rstrip(".") + " views"
    elif views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M".rstrip("0").rstrip(".") + " views"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K".rstrip("0").rstrip(".") + " views"
    return f"{views} views"

def format_duration(seconds):
    if seconds == None:
        return "Channel"
    minutes, sec = divmod(seconds, 60)
    return f"{int(minutes)}:{int(sec):02d}"

def search_youtube(query, max_results=20):
    ydl_opts = {
        'quiet': True,
        "skip_download": True,
        "dump_json": True,
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)

    print(result)
    
    return [(entry['title'], f"{entry.get('channel')} - {format_duration(entry.get('duration'))} - {shorten_views(entry.get('view_count'))}", entry.get('url'), entry['thumbnails'][-1]['url']) for entry in result['entries']]

def get_stream_url(youtube_url):
    ydl_opts = {
        'format': 'worst[ext=mp4]', # who needs 4k quality for a grid of 2 fucking pixels!!!
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']
    
async def get_video_info(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_get_video_info, url)

def sync_get_video_info(url):
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "views": info.get("view_count"),
            "channel": info.get("uploader"),
        }
