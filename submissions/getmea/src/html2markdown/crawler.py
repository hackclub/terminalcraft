# Note: Everything in this directory is a minified version of https://github.com/unclecode/crawl4ai/tree/main due to it's massive installation size


import requests

from html2markdown.markdown_generator import (
    DefaultMarkdownGenerator,
)


# Request html
def main(url: str):
    # Get raw html
    res = requests.get(url)
    res.encoding = "utf-8"
    html = res.text

    # Convert to markdown
    markdown_result: str = DefaultMarkdownGenerator().generate_markdown(
        html=html,
        url=url,
    )

    return markdown_result
