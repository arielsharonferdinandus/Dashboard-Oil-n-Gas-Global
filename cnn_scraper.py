import requests
from bs4 import BeautifulSoup
from datetime import datetime

CNN_SEARCH_URL = "https://www.cnn.com/search"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

KEYWORDS = [
    "oil",
    "gas",
    "energy",
    "crude",
    "opec",
    "fuel"
]


def scrape_cnn_news(query="oil gas", max_articles=8):
    params = {
        "q": query,
        "size": max_articles
    }

    response = requests.get(CNN_SEARCH_URL, params=params, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    articles = []

    for item in soup.select(".cnn-search__result")[:max_articles]:
        title_el = item.select_one(".cnn-search__result-headline a")
        summary_el = item.select_one(".cnn-search__result-body")
        date_el = item.select_one(".cnn-search__result-publish-date")

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        link = "https://www.cnn.com" + title_el["href"]
        summary = summary_el.get_text(strip=True) if summary_el else ""
        published = date_el.get_text(strip=True) if date_el else ""

        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "source": "CNN",
            "published": published
        })

    return articles
