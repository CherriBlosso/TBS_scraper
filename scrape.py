from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from typing import Optional
import os

class Article(BaseModel):
    url: str
    headline: str
    published_time: str
    content: str

def tbs_news_scraper(url: str) -> Article:
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Headline
    headline_tag = soup.find('h1')  # TBS uses <h1> for headlines
    if not headline_tag:
        raise ValueError(f"Headline not found at {url}")
    headline = headline_tag.get_text(strip=True)

    # Published time
    # TBS often uses <span class="time"> along with datetime attribute
    time_tag = soup.find('span', class_='time')
    if time_tag:
        published_time = time_tag.get_text(strip=True)
    else:
        # fallback to any <time> tag if available
        t = soup.find('time')
        published_time = t.get_text(strip=True) if t else "Unknown"

    # Content
    # The main story is often inside <div class="field-name-body"> or related container
    content_block = soup.find('div', class_='field-name-body') or soup.find('div', class_='post-content')
    content_paras = content_block.find_all('p') if content_block else soup.select('article p')
    content = '\n\n'.join([p.get_text(strip=True) for p in content_paras if p.get_text(strip=True)])

    return Article(url=url, headline=headline, published_time=published_time, content=content)

def save_article_markdown(article: Article, output_path="article.md"):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"# {article.headline}\n\n")
        f.write(f"**Published:** {article.published_time}\n\n")
        f.write(f"**Source:** [{article.url}]({article.url})\n\n")
        f.write(f"---\n\n{article.content.strip()}\n")
    print(f"✅ Article saved to {output_path}")

if __name__ == "__main__":
    url = "https://www.tbsnews.net/worldbiz/asia/taiwan-simulate-chinese-invasion-major-drill-1178041"
    article = tbs_news_scraper(url)
    save_article_markdown(article, "article.md")

