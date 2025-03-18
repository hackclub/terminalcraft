from googlesearch import search

def google_search(query, num_results=30):
    search_results = search(query, lang="en", num_results=num_results, advanced=True)
    listtogive = []
    for result in search_results:
        url = result.url
        if url == None or url == "":
            continue
        title = result.title
        description = result.description
        final = [url, title, description]
        listtogive.append(final)
    return listtogive

if __name__ == "__main__":
    search_query = input("Enter your search query: ")
    results = google_search(search_query, num_results=10)

