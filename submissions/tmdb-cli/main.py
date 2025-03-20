import argparse
from commands import trending, search, find, details, config
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser(description="Search for movies and TV shows using the TMDB API")
subparsers = parser.add_subparsers(dest="command", required=True)

# Config command
config_parser = subparsers.add_parser("config", help="Change app preferences")
config_parser.add_argument("set", choices=["api_key", "region", "base_url", "img_url"], help="What to set")
config_parser.add_argument("value", help="Value to set")
config_parser.set_defaults(func=config.set)

# Search command
search_parser = subparsers.add_parser("search", help="Search for a movie or TV show")
search_parser.add_argument("type", choices=["movie", "tv"], help="Search type (movie/tv)")
search_parser.add_argument("query", help="Title to search for")
search_parser.add_argument("-c", "--count", type=int, default=10, help="Number of results to show (default: 10)")
search_parser.add_argument("-p", "--page", type=int, default=1, help="Page number of search results to fetch (default: 1)")
search_parser.add_argument("--json", action="store_true", help="Save results to json")
search_parser.set_defaults(func=search.fetch)

# Trending command
trending_parser = subparsers.add_parser("trending", help="List trending movies or TV shows")
trending_parser.add_argument("type", choices=["movie", "tv"], help="Trending type (movie/tv)")
trending_parser.add_argument("-c", "--count", type=int, default=10, help="Number of results to show (default: 10)")
trending_parser.add_argument("-p", "--page", type=int, default=1, help="Page number of search results to fetch (default: 1)")
trending_parser.add_argument("--json", action="store_true", help="Save results to json")
trending_parser.set_defaults(func=trending.fetch)

# Details command
details_parser = subparsers.add_parser("details", help="Get movie/TV show details")
details_parser.add_argument("type", choices=["movie", "tv"], help="Movie or TV show")
details_parser.add_argument("id", help="The ID of the media to fetch")
details_parser.add_argument("--json", action="store_true", help="Save results to json")
details_parser.set_defaults(func=details.fetch)

# Find command
find_parser = subparsers.add_parser("find", help="Find movies/TV shows by external ID")
find_parser.add_argument("id", help="External ID to search for")
find_parser.add_argument("--imdb", action="store_true", help="Find by IMDb ID")
find_parser.add_argument("--facebook", action="store_true", help="Find by Facebook ID")
find_parser.add_argument("--instagram", action="store_true", help="Find by Instagram ID")
find_parser.add_argument("--tvdb", action="store_true", help="Find by TheTVDB ID")
find_parser.add_argument("--tiktok", action="store_true", help="Find by TikTok ID")
find_parser.add_argument("--wikidata", action="store_true", help="Find by Wikidata ID")
find_parser.add_argument("--youtube", action="store_true", help="Find by YouTube ID")
find_parser.add_argument("--count", type=int, default=10, help="Number of results to show (default: 10)")
find_parser.add_argument("--page", type=int, default=1, help="Page number of search results to fetch (default: 1)")
find_parser.add_argument("--json", action="store_true", help="Save results to json")
find_parser.set_defaults(func=find.fetch)

args = parser.parse_args()
args.func(args)