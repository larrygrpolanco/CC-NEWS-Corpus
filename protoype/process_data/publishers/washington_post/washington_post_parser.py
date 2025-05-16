def extract_washington_post_text(soup):
    """Extract main article text from Washington Post HTML"""
    # Customized for Washington Post articles
    article_content = soup.find('div', class_='article-body')
    if article_content:
        paragraphs = article_content.find_all('p')
        return '\n'.join(p.get_text() for p in paragraphs)
    else:
        return "No article content found"

def extract_washington_post_metadata(soup):
    """Extract metadata from Washington Post article"""
    metadata = {}
    title = soup.find('h1', class_='headline')
    if title:
        metadata['title'] = title.get_text().strip()
    
    author = soup.find('span', class_='author-name')
    if author:
        metadata['author'] = author.get_text().strip()
    
    date = soup.find('span', class_='publication-date')
    if date:
        metadata['date'] = date.get_text().strip()
    
    return metadata

def is_washington_post_politics(record):
    """Check if the record is from washingtonpost.com/politics"""
    url = record.rec_headers.get_header('WARC-Target-URI')
    return url is not None and 'washingtonpost.com/politics' in url

def main(warc_file):
    # Process WARC records with URL filtering
    with open(warc_file, 'rb') as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == 'response' and is_washington_post_politics(record):
                soup = BeautifulSoup(record.content_stream().read(), 'html.parser')
                text = extract_washington_post_text(soup)
                metadata = extract_washington_post_metadata(soup)
                with open('extracted_data_politics.txt', 'a') as output_file:
                    output_file.write(f"URL: {record.rec_headers.get_header('WARC-Target-URI')}\n")
                    output_file.write(f"Metadata: {metadata}\n")
                    output_file.write(f"Text: {text}\n\n")

if __name__ == "__main__":
    import sys
    from warcio.archiveiterator import ArchiveIterator
    from bs4 import BeautifulSoup
    
    if len(sys.argv) != 2:
        print("Usage: python washington_post_parser.py <warc_file>")
        sys.exit(1)
    
    warc_file = sys.argv[1]
    main(warc_file)
