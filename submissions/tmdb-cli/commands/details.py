import requests
from utils import environment, json, imgcat

def fetch(args):
    url = f"{environment.base_url()}/{args.type}/{args.id}?api_key={environment.api_key()}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # We don't use results.process because we want to customize what we show here
        title = data.get("title") or data.get("name")
        release_date = data.get("release_date") or data.get("first_air_date")
        overview = data.get("overview")
        popularity = data.get("popularity")
        vote_average = data.get("vote_average")
        vote_count = data.get("vote_count")
        poster_path = data.get("poster_path")

        if poster_path:
            imgcat.print(f"{environment.img_url()}{poster_path}")
        
        print(f"Title: {title}")
        print(f"Release Date: {release_date}")
        print(f"Overview: {overview}")
        print(f"Popularity: {popularity}")
        print(f"Vote Average: {vote_average} for {vote_count} votes")

        if args.json:
            json.save(data, "details.json")
    else:
        print(f"Failed to complete request with response code: {response.status_code}, {response.text}")