import re
import requests
from bs4 import BeautifulSoup


def extract_website_from_md(md_text):

    patterns = [
        r"https?://[^\s\)]+",
        r"www\.[^\s\)]+"
    ]

    for pattern in patterns:
        match = re.search(pattern, md_text, re.IGNORECASE)
        if match:
            url = match.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url

    return None


def scrape_public_data(URL):
  url = URL
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/120.0.0.0 Safari/537.36"
      )
  }

  response = requests.get(url, headers=headers, timeout=20)
  soup = BeautifulSoup(response.text, "html.parser")
  #print(soup.title.text)
  paragraphs = soup.find_all("p")

  text_blocks = []
  for p in paragraphs:
      text = p.get_text(strip=True)
      if len(text) > 50:
          text_blocks.append(text)

  public_text = " ".join(text_blocks)
  #print(public_text[:1000])

  pages = [
      "",
      "/about",
      "/about-us",
      "/products",
      "/services"
  ]
  collected_text = ""
  for page in pages:
      try:
          res = requests.get(url + page, timeout=10)
          soup = BeautifulSoup(res.text, "html.parser")
          for p in soup.find_all("p"):
              collected_text += p.get_text() + " "
      except:
          pass

  return {
      "raw_text": collected_text,
      "source_urls": [url + p for p in pages]
  }