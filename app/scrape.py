import requests
import re
import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json
from dotenv import load_dotenv

load_dotenv()

DISCOURSE_URL = "https://discourse.onlinedegree.iitm.ac.in"
FORUM_URL = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"
MD_BASE_URL = "https://tds.s-anand.net/"

TDS_KB_ID = 34
MD_SOURCES = {
    "https://tds.s-anand.net/2025-01/_sidebar.md",
    "https://tds.s-anand.net/2025-01/README.md"
}

DISCOURSE_COOKIES = {
    '_t': os.getenv('_T_COOKIE', ''),
    '_forum_session': os.getenv('_FORUM_SESSION', ''),
}

tds_md_links =[]
discourse_links = []

## Reference: https://discourse.onlinedegree.iitm.ac.in/t/using-browser-cookies-to-access-discourse-api-in-python/173605 
## for create_session and verify_authentication functions 
## ----------------------------------------------------------------------------

def create_session(cookies: dict) -> requests.Session:
    global discourse_session
    discourse_session = requests.Session()
    domain = DISCOURSE_URL.split("//")[1]
    for name, value in cookies.items():
        if not value:
            raise ValueError(f"Cookie '{name}' is empty.")
        discourse_session.cookies.set(name, value, domain=domain)
    return discourse_session

def verify_authentication(session: requests.Session):
    response = session.get(f"{DISCOURSE_URL}/session/current.json")
    if response.status_code == 200:
        user = response.json().get('current_user', {}).get('username')
        print(f"Authenticated as: {user}")
    else:
        raise Exception(f"Authentication failed using Cookies with status code: {response.status_code}")
    
## ----------------------------------------------------------------------------

## Scraping Links from TDS - Course Markdown Files
## ----------------------------------------------------------------------------

def resolve_link(link: str) -> str:
    if link.endswith(".md") and link.startswith("../"):
        return urljoin(MD_BASE_URL, link)
    else:
        return link
    
def get_links_from_markdown(url: str):
    print(f"Extracting links from: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    md = resp.text

    matches = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', md)
    for text, href in matches:
        full_url = resolve_link(href)
        if full_url.startswith("http") and any(domain in full_url for domain in ["tds.s-anand", "exam.sanand"]):
            tds_md_links.append({"title": text.strip(), "url": full_url})
        elif full_url.startswith(DISCOURSE_URL):
            discourse_links.append({"title": text.strip(), "url": full_url})

## --------------------------------------------------------------------------------

## Scraping Links from Discourse - TDS Project Forum
## --------------------------------------------------------------------------------
def get_links_from_discouse_forum():
    print(f"Extracting links from: {FORUM_URL}")
    article = fetch_article_content(FORUM_URL, return_html=True)
    # print(article)
    for link in article.find_all("a", href=True, class_="title"):
        title = link.get_text(strip=True)
        url = link['href']
        discourse_links.append({"title": title, "url": url})

## --------------------------------------------------------------------------------

## Fetching Article Content
## --------------------------------------------------------------------------------

def fetch_article_content(article_url: str, return_html: bool = False):
    try:
        # response.raise_for_status()
        # content_type = response.headers.get('Content-Type', '')

        if article_url.endswith(".md"):
            response = requests.get(article_url, timeout=10)
            print(f"Fetching article: {article_url}")
            response.raise_for_status() 
            return response.text.strip()
        
        elif article_url.startswith(DISCOURSE_URL):
            response = discourse_session.get(article_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            if return_html:
                return soup
            else:
                script_tag = soup.find('script', type='application/ld+json')
                if script_tag:
                    json_data = json.loads(script_tag.string)
                    main_entity = json_data.get("mainEntity", {})
                    date_published = main_entity.get("datePublished", None)
                    if date_published > "2025-01-01" and date_published < "2025-05-01":
                        print(f"Fetching article: {article_url}")
                        clean_text = ' '.join(' '.join(soup.get_text().splitlines()).strip().split())
                        return clean_text
                    return None
                else:
                    print(f"Fetching article: {article_url}")
                    clean_text = ' '.join(' '.join(soup.get_text().splitlines()).strip().split())
                    return clean_text
        else:
            return None
        
    except Exception as e:
        if e is requests.exceptions.InvalidURL:
            print(f"Invalid URL: {article_url}")
        else:
            print(f"Unable to fetch {article_url}: {e.__class__.__name__}")
        return None

## Function to scrape TDS data
## --------------------------------------------------------------------------------

def scrape_data_tds_project():

    for source_url in MD_SOURCES:
        get_links_from_markdown(source_url)
    
    discourse_session = create_session(DISCOURSE_COOKIES)
    verify_authentication(discourse_session)
    get_links_from_discouse_forum()

    all_links_dict = {link["url"]: link for link in tds_md_links}

    for link in discourse_links:
        all_links_dict.setdefault(link["url"], link)

    all_links = list(all_links_dict.values())

    rag_documents = []
    id: int = 0
    for pair in all_links:
        title = pair.get("title")
        url = pair.get("url")
        content = fetch_article_content(url)
        if content:
            id += 1
            rag_documents.append({
                "id": id,
                "title": title,
                "url": url,
                "content": content
            })

    output_file = "articles_rag.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(rag_documents, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(rag_documents)} documents to {output_file}")

if __name__ == "__main__":
    scrape_data_tds_project()
    print("Scraping completed.")