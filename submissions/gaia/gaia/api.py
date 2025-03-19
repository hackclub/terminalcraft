import requests 
from bs4 import BeautifulSoup 
from fake_useragent import UserAgent

class PlusSearchRequest:
    def __init__(self, query, search_type="title", headers=None):
        self.query = query
        self.search_type = search_type
        self.col_names = [
            "Title",
            "Author",
            "Publisher",
            "Year",
            "Pages",
            "Language",
            "Size",
            "Extension",
            "Mirror_1",
            "Mirror_2",
            "Mirror_3",
            "Mirror_4",
            "Mirror_5",
        ]
        self.headers = headers

        if len(self.query) < 3:
            raise Exception("Query is too short")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_page(self, page=1):
        query_parsed = "%20".join(self.query.split(" "))
        if self.search_type.lower() == "title":
            search_url = (
                f"https://libgen.li/index.php?req={query_parsed}&columns%5B%5D=t&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&topics%5B%5D=r&res=25&filesuns=all&page={page}"
            )
        elif self.search_type.lower() == "author":
            search_url = (
                f"https://libgen.li/index.php?req={query_parsed}&columns%5B%5D=a&objects%5B%5D=f&objects%5B%5D=e&objects%5B%5D=s&objects%5B%5D=a&objects%5B%5D=p&objects%5B%5D=w&topics%5B%5D=l&topics%5B%5D=r&res=25&filesuns=allpage={page}"
            )
        search_page = requests.get(search_url, headers=self.headers)
        return search_page

    def aggregate_request_data(self, page=1):
        search_page = self.get_search_page(page)
        soup = BeautifulSoup(search_page.text, "lxml")
        self.strip_i_tag_from_soup(soup)

        information_table = soup.find("table", {"id": "tablelibgen"})

        raw_data = []
        for row in information_table.find_all("tr")[1:]:
            tds = row.find_all("td")
            title = ""

            # EXTRACTING TITLE
            for a in tds[0].find_all("a", href=True):
                if not any(parent.name in ["b", "i"] for parent in a.parents):
                    title = a.get_text(strip=True)
                    break 

            contents = [title]
            for td in tds[1:]:
                if td.find("a") and td.find("a").has_attr("title"):
                    contents.append(td.a["href"])
                else:
                    contents.append("".join(td.stripped_strings))

            raw_data.append(contents)

        output_data = [dict(zip(self.col_names, row)) for row in raw_data]
        return output_data

class SearchRequest:
    def __init__(self, query, search_type="title", headers=None):
        self.query = query
        self.search_type = search_type
        self.col_names = [
            "ID",
            "Author",
            "Title",
            "Publisher",
            "Year",
            "Pages",
            "Language",
            "Size",
            "Extension",
            "Mirror_1",
            "Mirror_2",
            "Mirror_3",
            "Mirror_4",
            "Mirror_5",
            "Edit",
        ]
        self.headers = headers

        if len(self.query) < 3:
            raise Exception("Query is too short")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
        if self.search_type.lower() == "title":
            search_url = (
                f"https://libgen.is/search.php?req={query_parsed}&column=title"
            )
        elif self.search_type.lower() == "author":
            search_url = (
                f"https://libgen.is/search.php?req={query_parsed}&column=author"
            )
        search_page = requests.get(search_url)
        return search_page

    def aggregate_request_data(self, page=1):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "lxml")
        self.strip_i_tag_from_soup(soup)

        # Libgen results contain 3 tables
        # Table2: Table of data to scrape.
        information_table = soup.find_all("table")[2]

        # Determines whether the link url (for the mirror)
        # or link text (for the title) should be preserved.
        # Both the book title and mirror links have a "title" attribute,
        # but only the mirror links have it filled.(title vs title="libgen.io")
        raw_data = [
            [
                td.a["href"]
                if td.find("a")
                and td.find("a").has_attr("title")
                and td.find("a")["title"] != ""
                else "".join(td.stripped_strings)
                for td in row.find_all("td")
            ]
            for row in information_table.find_all("tr")[
                1:
            ]  # Skip row 0 as it is the headings row
        ]

        output_data = [dict(zip(self.col_names, row)) for row in raw_data]
        return output_data


MIRROR_SOURCES = ["GET", "Cloudflare", "IPFS.io", "Infura"]

class LibgenSearch:
    def __init__(self, is_plus=False):
        self.is_plus = is_plus 
        self.ua = UserAgent()
        self.ua_head = {"User-Agent": str(self.ua.firefox)}

    def search_title(self, query, page=1):
        if self.is_plus:
            search_request = PlusSearchRequest(query, search_type="title", headers=self.ua_head)
        else:
            search_request = SearchRequest(query, search_type="title", headers=self.ua_head)
        return search_request.aggregate_request_data(page)

    def search_author(self, query, page=1):
        if self.is_plus:
            search_request = PlusSearchRequest(query, search_type="author", headers=self.ua_head)
        else:
            search_request = SearchRequest(query, search_type="author", headers=self.ua_head)
        return search_request.aggregate_request_data(page)

    def search_title_filtered(self, query, filters, exact_match=True, page=1):
        if self.is_plus:
            search_request = PlusSearchRequest(query, search_type="title", headers=self.ua_head)
        else:
            search_request = SearchRequest(query, search_type="title", headers=self.ua_head)
        results = search_request.aggregate_request_data(page)
        filtered_results = filter_results(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results

    def search_author_filtered(self, query, filters, exact_match=True, page=1):
        if self.is_plus:
            search_request = PlusSearchRequest(query, search_type="author", headers=self.ua_head)
        else:
            search_request = SearchRequest(query, search_type="author", headers=self.ua_head)
        results = search_request.aggregate_request_data(page)
        filtered_results = filter_results(
            results=results, filters=filters, exact_match=exact_match
        )
        return filtered_results

    def resolve_download_links(self, item):
        mirror_1 = item["Mirror_1"]
        if self.is_plus:
            page = requests.get(f"https://libgen.li/{mirror_1}", headers=self.ua_head)
        else:
            page = requests.get(mirror_1)
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all("a", string=MIRROR_SOURCES)

        if self.is_plus:
            download_links = {link.string: f"https://libgen.li/{link['href']}" for link in links}
        else:
            download_links = {link.string: link["href"] for link in links}
    
        return download_links


def filter_results(results, filters, exact_match):
    """
    Returns a list of results that match the given filter criteria.
    When exact_match = true, we only include results that exactly match
    the filters (ie. the filters are an exact subset of the result).

    When exact-match = false,
    we run a case-insensitive check between each filter field and each result.

    exact_match defaults to TRUE -
    this is to maintain consistency with older versions of this library.
    """

    filtered_list = []
    if exact_match:
        for result in results:
            # check whether a candidate result matches the given filters
            if filters.items() <= result.items():
                filtered_list.append(result)

    else:
        filter_matches_result = False
        for result in results:
            for field, query in filters.items():
                if query.casefold() in result[field].casefold():
                    filter_matches_result = True
                else:
                    filter_matches_result = False
                    break
            if filter_matches_result:
                filtered_list.append(result)
    return filtered_list
