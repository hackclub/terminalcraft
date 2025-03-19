from duckduckgo_search import DDGS


CAPTURE = ["NAME", "ID", "ID_LIKE", "VERSION"]


def get_linux_flavor():
    """Returns minified output similar to cat /etc/os-release"""

    res: list[str] = []

    with open("/etc/os-release", "r") as f:
        for line in f.readlines():
            if line.split("=")[0] in CAPTURE:
                res.append(line)

    return res


def search_duck_duck(query: str):
    results = DDGS().text(query, max_results=5)

    res_str = ""

    for res in results:
        res_str += f"""- Title: {res['title']}\n  URL: {res['href']}\n  Description: {res['body']}\n"""

    return res_str
