import warcio
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

def process_warc_file(warc_path, target_domain):
    """
    Process a WARC file and extract articles from specified domain
    Args:
        warc_path: Path to WARC file
        target_domain: Domain to filter articles from (e.g. 'washingtonpost.com')
    Returns:
        List of dictionaries containing article metadata and text
    """
    articles = []
    
    with open(warc_path, 'rb') as stream:
        for record in warcio.ArchiveIterator(stream):
            if record.rec_type == 'response':
                url = record.rec_headers.get_header('WARC-Target-URI')
                if target_domain in url:
                    try:
                        html = record.content_stream().read()
                        soup = BeautifulSoup(html, 'lxml')
                        
                        article = {
                            'url': url,
                            'date': record.rec_headers.get_header('WARC-Date'),
                            'title': extract_title(soup),
                            'text': extract_text(soup)
                        }
                        articles.append(article)
                    except Exception as e:
                        print(f"Error processing {url}: {str(e)}")
    
    return articles

def extract_title(soup):
    """Extract article title from HTML"""
    title = soup.find('title')
    return title.get_text() if title else 'No title found'

def extract_text(soup):
    """Extract main article text from HTML"""
    # This will be customized per publisher
    paragraphs = soup.find_all('p')
    return '\n'.join(p.get_text() for p in paragraphs)
