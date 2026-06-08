# Minified version from https://github.com/deedy5/duckduckgo_search/tree/main

from __future__ import annotations

from time import sleep, time
from typing import Any, Literal

from lxml.etree import _Element
from lxml.html import HTMLParser as LHTMLParser
from lxml.html import document_fromstring
from html import unescape

import re
import requests
from urllib.parse import unquote

REGEX_STRIP_TAGS = re.compile("<.*?>")


def _normalize(raw_html: str) -> str:
    """Strip HTML tags from the raw_html string."""
    return unescape(REGEX_STRIP_TAGS.sub("", raw_html)) if raw_html else ""


def _normalize_url(url: str) -> str:
    """Unquote URL and replace spaces with '+'."""
    return unquote(url).replace(" ", "+") if url else ""


class DDGS:
    """DuckDuckgo_search class to get search results from duckduckgo.com."""

    timeout = 10

    def _get_url(
        self,
        url: str,
        data: dict[str, str] | None = None,
    ) -> Any:
        resp = requests.post(
            url=url,
            timeout=self.timeout,
            data=data,
        )

        if resp.status_code == 200:
            return resp.text

    def text(
        self,
        keywords: str,
        region: str = "wt-wt",
        timelimit: str | None = None,
        max_results: int | None = None,
    ) -> list[dict[str, str]]:

        results = self._text_html(keywords, region, timelimit, max_results)

        return results

    def _text_html(
        self,
        keywords: str,
        region: str = "wt-wt",
        timelimit: str | None = None,
        max_results: int | None = None,
    ) -> list[dict[str, str]]:
        assert keywords, "keywords is mandatory"

        payload = {
            "q": keywords,
            "b": "",
            "kl": region,
        }
        if timelimit:
            payload["df"] = timelimit

        cache = set()
        results: list[dict[str, str]] = []

        for _ in range(5):
            resp_content = self._get_url(
                "https://html.duckduckgo.com/html", data=payload
            )
            if "No  results." in resp_content:
                return results

            tree = document_fromstring(
                resp_content,
                LHTMLParser(
                    remove_blank_text=True,
                    remove_comments=True,
                    remove_pis=True,
                    collect_ids=False,
                ),
            )
            elements = tree.xpath("//div[h2]")
            if not isinstance(elements, list):
                return results

            for e in elements:
                if isinstance(e, _Element):
                    hrefxpath = e.xpath("./a/@href")
                    href = (
                        str(hrefxpath[0])
                        if hrefxpath and isinstance(hrefxpath, list)
                        else None
                    )
                    if (
                        href
                        and href not in cache
                        and not href.startswith(
                            (
                                "http://www.google.com/search?q=",
                                "https://duckduckgo.com/y.js?ad_domain",
                            )
                        )
                    ):
                        cache.add(href)
                        titlexpath = e.xpath("./h2/a/text()")
                        title = (
                            str(titlexpath[0])
                            if titlexpath and isinstance(titlexpath, list)
                            else ""
                        )
                        bodyxpath = e.xpath("./a//text()")
                        body = (
                            "".join(str(x) for x in bodyxpath)
                            if bodyxpath and isinstance(bodyxpath, list)
                            else ""
                        )
                        results.append(
                            {
                                "title": _normalize(title),
                                "href": _normalize_url(href),
                                "body": _normalize(body),
                            }
                        )
                        if max_results and len(results) >= max_results:
                            return results

            npx = tree.xpath('.//div[@class="nav-link"]')
            if not npx or not max_results:
                return results

            next_page = npx[-1] if isinstance(npx, list) else None

            if isinstance(next_page, _Element):
                names = next_page.xpath('.//input[@type="hidden"]/@name')
                values = next_page.xpath('.//input[@type="hidden"]/@value')
                if isinstance(names, list) and isinstance(values, list):
                    payload = {str(n): str(v) for n, v in zip(names, values)}

        return results
