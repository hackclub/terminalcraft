from utils import environment, json, results
import requests

def fetch(args):
    API_KEY = environment.get_api_key()
    BASE_URL = environment.base_url()
    REGION = environment.region()
    
    url = f"{BASE_URL}/trending/{args.type}/day?api_key={API_KEY}&page={args.page}&region={REGION}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        results_list = data.get("results", [])
        if not results_list:
            print("No results found")
            return
        
        results.process(results_list)

        if args.json:
            json.save(data, "trending.json")
    else:
        print(f"Failed to complete request with response code: {response.status_code}, {response.text}")