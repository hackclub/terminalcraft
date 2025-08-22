from utils import imgcat, environment

def process(results, total):
    for item in results[:total]:
        id = item.get("id")
        title = item.get("title") or item.get("name")
        release_date = item.get("release_date") or item.get("first_air_date")
        poster_path = item.get("poster_path")
        
        if poster_path:
            imgcat.print(f"{environment.img_url()}{poster_path}")
        
        print(f"Title: {title}")
        print(f"Release Date: {release_date}")
        print(f"ID: {id}")
        print("") # spacing
        print("="*40)