#!/usr/bin/env python3
import sys, requests, time, os, asyncio, re, random
from concurrent.futures import ThreadPoolExecutor

FAST_MODE = False
HUMAN_MODE = False

USED_BROWSERS = {}

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  
        r'localhost|'  
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' 
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  
        r'(?::\d+)?'  
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def send_request(url):
    try:
        if HUMAN_MODE:
            delay = random.uniform(0.5, 2.0)
            time.sleep(delay)
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/92.0.4515.107 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/91.0.4472.114 Safari/537.36"
            ]
            ua = random.choice(user_agents)
            USED_BROWSERS[ua] = USED_BROWSERS.get(ua, 0) + 1
            headers = {"User-Agent": ua}
        else:
            headers = {"User-Agent": "Mozilla/5.0"}
        timeout = 3 if FAST_MODE else 10
        response = requests.get(url, timeout=timeout, headers=headers)
        return response.status_code == 200
    except Exception:
        return False

async def run_requests(executor, total_times, url):
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(executor, send_request, url) for _ in range(total_times)]
    completed = 0
    results = []
    for fut in asyncio.as_completed(tasks):
        result = await fut
        results.append(result)
        completed += 1
        progress = (completed / total_times) * 100
        filled_len = int(30 * completed / total_times)
        bar = "#" * filled_len + "-" * (30 - filled_len)
        sys.stdout.write(f"\rProgress: [{bar}] {progress:.2f}% complete")
        sys.stdout.flush()
    print()
    return total_times, sum(results)

async def run_requests_rate(executor, total_times, url, rate):
    req_count = 0
    success_count = 0
    loop = asyncio.get_event_loop()
    while req_count < total_times:
        batch = min(rate, total_times - req_count)
        tasks = [loop.run_in_executor(executor, send_request, url) for _ in range(batch)]
        results = await asyncio.gather(*tasks)
        req_count += batch
        success_count += sum(results)
        progress = (req_count / total_times) * 100
        filled_len = int(30 * req_count / total_times)
        bar = "#" * filled_len + "-" * (30 - filled_len)
        sys.stdout.write(f"\rProgress: [{bar}] {progress:.2f}% complete")
        sys.stdout.flush()
    print()
    return req_count, success_count

def main():
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "help":
        print("Usage: dosper  <url> <times> <mode> [rate] (optional)")
        print("  url   - Target URL , with \"quotation marks\" ")
        print("  times - Number of requests to send")
        print("  mode  - Execution mode: F (Fast), H (Human), R (Rate-limited)")
        print("  rate  - Rate limit per second (only for R mode)")
        print("Examples:")
        print("doseper \"https://example.com\" 100 R 10")
        print("doseper \"https://example.com\" 100 H")
        return

    if len(sys.argv) < 4:
        print("Usage: doseper <url> <times> <mode> [rate] (optional)")
        return

    url = sys.argv[1]
    total_times = int(sys.argv[2])
    
    if not is_valid_url(url):
        print("Please enter a valid URL")
        return

    mode = sys.argv[3].upper()
    rate = None
    input_rate_str = None

    if mode == "R":
        if len(sys.argv) < 5:
            print("Usage: surge <url> <times> R <rate>")
            return
        input_rate_str = sys.argv[4]
        try:
            rate = int(input_rate_str)
            if rate > 50:
                rate = 50
        except ValueError:
            print("Please enter a valid rate")
            return

    if mode == "H":
        HUMAN_MODE = True
        FAST_MODE = False
    elif mode in ("F", "R"):
        FAST_MODE = True
        HUMAN_MODE = False
    else:
        print("Unknown mode, please use F, H, R")
        return

    msg = {
        "website": f"Website to test: {url}",
        "num_requests": f"Number of requests: {total_times}",
        "execution_mode": "Execution mode: " + ("Human mode (H)" if HUMAN_MODE else ("Rate-limited mode (R)" if mode == "R" else "Fast mode (F)")),
        "max_rate": ("Max rate: " + input_rate_str) if mode == "R" else "",
        "confirm": "Confirm the above information (Y to continue, any other key to cancel): ",
        "cancel": "Operation canceled",
        "completed": "Completed {} requests, {} succeeded",
        "total_time": "Total execution time: {} seconds"
    }

    print(msg["website"])
    print(msg["num_requests"])
    print(msg["execution_mode"])
    if msg["max_rate"]:
        print(msg["max_rate"])

    confirm = input(msg["confirm"])
    if confirm.upper() != "Y":
        print(msg["cancel"])
        return

    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        if mode == "R":
            req_count, success_count = asyncio.run(run_requests_rate(executor, total_times, url, rate))
        else:
            req_count, success_count = asyncio.run(run_requests(executor, total_times, url))
    
    print("\n" + msg["completed"].format(req_count, success_count))
    elapsed = round(time.time() - start_time, 2)
    print(msg["total_time"].format(elapsed))
    
if __name__ == "__main__":
    main()