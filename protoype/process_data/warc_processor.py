import warcio
from bs4 import BeautifulSoup
from publishers.washington_post.washington_post_parser import extract_washington_post_text, extract_washington_post_metadata

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

                        if 'washingtonpost.com' in url:
                            article = {
                                'url': url,
                                'date': record.rec_headers.get_header('WARC-Date'),
                                'metadata': extract_washington_post_metadata(soup),
                                'text': extract_washington_post_text(soup)
                            }
                        else:
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

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process WARC file and extract articles')
    parser.add_argument('warc_path', help='Path to WARC file')
    parser.add_argument('target_domain', help='Domain to filter articles from (e.g. washingtonpost.com)')
    args = parser.parse_args()

    articles = process_warc_file(args.warc_path, args.target_domain)
    for article in articles:
        print(f"URL: {article['url']}")
        if 'metadata' in article:
            print("Metadata:")
            for key, value in article['metadata'].items():
                print(f"{key.capitalize()}: {value}")
        else:
            print(f"Title: {article['title']}")
        print("Text:")
        print(article['text'])
        print("-" * 80)
