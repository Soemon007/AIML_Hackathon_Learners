import re
import requests
from bs4 import BeautifulSoup

def extract_website_from_md(md_text):  # Takes URL from .md file
    patterns = [
        r"https?://[^\s\)]+",
        r"www\.[^\s\)]+"
    ]
    for pattern in patterns:
        match = re.search(pattern, md_text, re.IGNORECASE)
        if match:
            url = match.group(0).strip()
            # Remove URL fragments and query params
            url = url.split('#')[0].split('?')[0]
            if not url.startswith("http"):
                url = "https://" + url
            return url
    return None

def scrape_public_data(URL):  # AScrapes the extracted URL
    url = URL
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()  # Verify response was successful
    except requests.RequestException as e:
        return {"raw_text": "", "source_urls": [], "error": str(e)}
    
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")
    text_blocks = []
    
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 50:
            text_blocks.append(text)
    
    public_text = " ".join(text_blocks)
    
    pages = [
        "",
        "/about",
        "/about-us",
        "/products",
        "/services"
    ]
    
    collected_text = ""
    successful_urls = []
    
    for page in pages:
        try:
            res = requests.get(url + page, timeout=10, headers=headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            for p in soup.find_all("p"):
                text = p.get_text(strip=True)
                if len(text) > 50:  # Filter out short paragraphs
                    collected_text += text + " "
            successful_urls.append(url + page)
        except:
            pass
    
    # Limits text length to avoid memory issues
    collected_text = collected_text[:100000] if len(collected_text) > 100000 else collected_text
    
    return {
        "raw_text": collected_text.strip(),
        "source_urls": successful_urls
    }
