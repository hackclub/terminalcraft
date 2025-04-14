import requests
from utils import environment, json, results

def fetch(args):
    url = f"{environment.base_url()}/search/{args.type}?api_key={environment.api_key()}&query={args.query}&page={args.page}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        results_list = data.get("results", [])
        if not results_list:
            print("No results found")
            return
        
        result_count = getattr(args, "count", 10)
        results.process(results_list, result_count)

        if args.json:
            json.save(data, "search.json")
    else:
        print(f"Failed to complete request with response code: {response.status_code}, {response.text}")