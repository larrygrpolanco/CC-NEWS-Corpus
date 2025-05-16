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
