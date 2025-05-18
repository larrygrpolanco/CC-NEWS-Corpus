"""
HTML structure analyzer for examining content from political sources.
"""

import re
from bs4 import BeautifulSoup
import logging
from collections import Counter
from urllib.parse import urlparse
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HTMLAnalyzer:
    """
    Analyzes HTML content to determine structure and extractability of key elements.
    """
    
    def __init__(self, html_content, url=None):
        """
        Initialize the analyzer with HTML content.
        
        Args:
            html_content (str): The HTML content to analyze
            url (str, optional): The URL the content was fetched from
        """
        self.html = html_content
        self.url = url
        self.domain = urlparse(url).netloc if url else None
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.analysis = {}
    
    def analyze(self):
        """
        Perform a comprehensive analysis of the HTML structure.
        
        Returns:
            dict: Analysis results
        """
        self.analysis = {
            "url": self.url,
            "domain": self.domain,
            "content_type": self._determine_content_type(),
            "metadata": self._analyze_metadata(),
            "content_structure": self._analyze_content_structure(),
            "extractability": self._assess_extractability()
        }
        
        return self.analysis
    
    def _determine_content_type(self):
        """
        Determine if the page is an article, homepage, section page, etc.
        
        Returns:
            str: The content type
        """
        # Check for common article indicators
        article_indicators = [
            # Title patterns
            self.soup.find('h1'),
            self.soup.find(class_=re.compile(r'article-title|post-title|entry-title|headline')),
            self.soup.find(id=re.compile(r'article-title|post-title|entry-title|headline')),
            
            # Author patterns
            self.soup.find(class_=re.compile(r'author|byline')),
            self.soup.find(rel="author"),
            
            # Date patterns
            self.soup.find(class_=re.compile(r'date|published|posted|time')),
            self.soup.find('time'),
            
            # Content patterns
            self.soup.find(class_=re.compile(r'article-body|post-content|entry-content|story-body')),
            self.soup.find(id=re.compile(r'article-body|post-content|entry-content|story-body'))
        ]
        
        # Count how many article indicators we found
        indicator_count = sum(1 for i in article_indicators if i is not None)
        
        # Check for homepage indicators
        homepage_indicators = [
            # Multiple article links
            len(self.soup.find_all('a', href=re.compile(r'article|story|post|news'))) > 5,
            
            # Section headings
            len(self.soup.find_all(['h2', 'h3'], text=re.compile(r'Latest|Top|Featured|News|Opinion'))) > 0,
            
            # Navigation elements
            self.soup.find(class_=re.compile(r'nav|menu|navigation')),
            self.soup.find(id=re.compile(r'nav|menu|navigation')),
            
            # Multiple cards or teasers
            len(self.soup.find_all(class_=re.compile(r'card|teaser|thumbnail'))) > 3
        ]
        
        # Count how many homepage indicators we found
        homepage_count = sum(1 for i in homepage_indicators if i)
        
        # Make a determination
        if indicator_count >= 3:
            return "article"
        elif homepage_count >= 3:
            return "homepage"
        elif self.url and '/search' in self.url.lower():
            return "search_results"
        elif self.url and any(section in self.url.lower() for section in ['/category/', '/section/', '/topic/', '/tag/']):
            return "section_page"
        else:
            return "unknown"
    
    def _analyze_metadata(self):
        """
        Analyze metadata elements in the HTML.
        
        Returns:
            dict: Metadata analysis results
        """
        metadata = {}
        
        # Title analysis
        title_candidates = [
            self.soup.title.text.strip() if self.soup.title else None,
            self.soup.find('meta', property='og:title').get('content') if self.soup.find('meta', property='og:title') else None,
            self.soup.find('meta', name='twitter:title').get('content') if self.soup.find('meta', name='twitter:title') else None,
            self.soup.find('h1').text.strip() if self.soup.find('h1') else None,
            self.soup.find(class_=re.compile(r'article-title|post-title|entry-title|headline')).text.strip() 
                if self.soup.find(class_=re.compile(r'article-title|post-title|entry-title|headline')) else None,
        ]
        
        title_candidates = [t for t in title_candidates if t]
        
        metadata['title'] = {
            'found': len(title_candidates) > 0,
            'candidates': title_candidates,
            'best_candidate': title_candidates[0] if title_candidates else None,
            'selectors': self._get_selectors_for_element('title')
        }
        
        # Author analysis
        author_candidates = []
        
        # Check meta tags
        meta_author = self.soup.find('meta', attrs={'name': 'author'})
        if meta_author and meta_author.get('content'):
            author_candidates.append(meta_author.get('content'))
        
        # Check for author elements
        for author_elem in self.soup.find_all(['a', 'span', 'div', 'p'], class_=re.compile(r'author|byline')):
            author_text = author_elem.text.strip()
            if author_text and len(author_text) < 100:  # Avoid capturing large blocks
                author_candidates.append(author_text)
        
        # Check for rel="author"
        rel_author = self.soup.find(rel="author")
        if rel_author:
            author_candidates.append(rel_author.text.strip())
        
        metadata['author'] = {
            'found': len(author_candidates) > 0,
            'candidates': author_candidates,
            'best_candidate': author_candidates[0] if author_candidates else None,
            'selectors': self._get_selectors_for_element('author')
        }
        
        # Date analysis
        date_candidates = []
        
        # Check meta tags
        meta_date = self.soup.find('meta', property='article:published_time')
        if meta_date and meta_date.get('content'):
            date_candidates.append(meta_date.get('content'))
        
        # Check for time elements
        for time_elem in self.soup.find_all('time'):
            if time_elem.get('datetime'):
                date_candidates.append(time_elem.get('datetime'))
            elif time_elem.text.strip():
                date_candidates.append(time_elem.text.strip())
        
        # Check for date classes
        for date_elem in self.soup.find_all(class_=re.compile(r'date|published|posted|time')):
            date_text = date_elem.text.strip()
            if date_text and len(date_text) < 50:  # Avoid capturing large blocks
                date_candidates.append(date_text)
        
        metadata['date'] = {
            'found': len(date_candidates) > 0,
            'candidates': date_candidates,
            'best_candidate': date_candidates[0] if date_candidates else None,
            'selectors': self._get_selectors_for_element('date')
        }
        
        # Section/category analysis
        section_candidates = []
        
        # Check meta tags
        meta_section = self.soup.find('meta', property='article:section')
        if meta_section and meta_section.get('content'):
            section_candidates.append(meta_section.get('content'))
        
        # Check for breadcrumbs
        breadcrumbs = self.soup.find(class_=re.compile(r'breadcrumb'))
        if breadcrumbs:
            for link in breadcrumbs.find_all('a'):
                section_candidates.append(link.text.strip())
        
        # Check URL for section info
        if self.url:
            url_parts = self.url.split('/')
            for section_indicator in ['category', 'section', 'topic', 'tag']:
                if section_indicator in url_parts:
                    idx = url_parts.index(section_indicator)
                    if idx + 1 < len(url_parts) and url_parts[idx + 1]:
                        section_candidates.append(url_parts[idx + 1].replace('-', ' ').replace('_', ' ').title())
        
        metadata['section'] = {
            'found': len(section_candidates) > 0,
            'candidates': section_candidates,
            'best_candidate': section_candidates[0] if section_candidates else None,
            'selectors': self._get_selectors_for_element('section')
        }
        
        return metadata
    
    def _analyze_content_structure(self):
        """
        Analyze the structure of the main content.
        
        Returns:
            dict: Content structure analysis
        """
        structure = {}
        
        # Find potential content containers
        content_containers = [
            self.soup.find(class_=re.compile(r'article-body|post-content|entry-content|story-body')),
            self.soup.find(id=re.compile(r'article-body|post-content|entry-content|story-body')),
            self.soup.find('article'),
            self.soup.find(class_=re.compile(r'article|post|entry|story'))
        ]
        
        # Filter out None values
        content_containers = [c for c in content_containers if c]
        
        if not content_containers:
            structure['content_found'] = False
            structure['content_selectors'] = []
            structure['paragraph_count'] = 0
            structure['has_images'] = False
            structure['has_links'] = False
            structure['has_blockquotes'] = False
            structure['has_lists'] = False
            structure['has_tables'] = False
            structure['has_iframes'] = False
            return structure
        
        # Use the first container found
        container = content_containers[0]
        
        # Get selectors for the container
        selectors = []
        if container.get('id'):
            selectors.append(f"#{container.get('id')}")
        if container.get('class'):
            selectors.append(f".{'.'.join(container.get('class'))}")
        if not selectors:
            selectors.append(container.name)
        
        # Count paragraphs
        paragraphs = container.find_all('p')
        
        # Check for various content elements
        structure['content_found'] = True
        structure['content_selectors'] = selectors
        structure['paragraph_count'] = len(paragraphs)
        structure['has_images'] = len(container.find_all('img')) > 0
        structure['has_links'] = len(container.find_all('a')) > 0
        structure['has_blockquotes'] = len(container.find_all('blockquote')) > 0
        structure['has_lists'] = len(container.find_all(['ul', 'ol'])) > 0
        structure['has_tables'] = len(container.find_all('table')) > 0
        structure['has_iframes'] = len(container.find_all('iframe')) > 0
        
        # Analyze text content
        if paragraphs:
            text_content = ' '.join(p.text.strip() for p in paragraphs)
            structure['text_length'] = len(text_content)
            structure['word_count'] = len(text_content.split())
            structure['avg_paragraph_length'] = structure['word_count'] / len(paragraphs)
        else:
            structure['text_length'] = 0
            structure['word_count'] = 0
            structure['avg_paragraph_length'] = 0
        
        return structure
    
    def _assess_extractability(self):
        """
        Assess how easily content can be extracted from this HTML.
        
        Returns:
            dict: Extractability assessment
        """
        extractability = {}
        
        # Check if we found the key elements
        metadata_found = all([
            self.analysis.get('metadata', {}).get('title', {}).get('found', False),
            self.analysis.get('metadata', {}).get('date', {}).get('found', False)
        ])
        
        content_found = self.analysis.get('content_structure', {}).get('content_found', False)
        
        # Calculate an overall score
        score = 0
        
        if metadata_found:
            score += 50  # 50% of the score is for metadata
        
        if content_found:
            # Base points for finding content
            score += 25
            
            # Additional points based on content quality
            paragraph_count = self.analysis.get('content_structure', {}).get('paragraph_count', 0)
            if paragraph_count >= 5:
                score += 15
            elif paragraph_count >= 3:
                score += 10
            elif paragraph_count >= 1:
                score += 5
            
            # Penalize for very short content
            word_count = self.analysis.get('content_structure', {}).get('word_count', 0)
            if word_count < 100:
                score -= 10
        
        # Determine difficulty level
        if score >= 80:
            difficulty = "easy"
        elif score >= 60:
            difficulty = "moderate"
        elif score >= 40:
            difficulty = "challenging"
        else:
            difficulty = "difficult"
        
        extractability['score'] = score
        extractability['difficulty'] = difficulty
        extractability['metadata_complete'] = metadata_found
        extractability['content_extractable'] = content_found
        extractability['missing_elements'] = []
        
        # Identify missing elements
        if not self.analysis.get('metadata', {}).get('title', {}).get('found', False):
            extractability['missing_elements'].append('title')
        if not self.analysis.get('metadata', {}).get('author', {}).get('found', False):
            extractability['missing_elements'].append('author')
        if not self.analysis.get('metadata', {}).get('date', {}).get('found', False):
            extractability['missing_elements'].append('date')
        if not content_found:
            extractability['missing_elements'].append('content')
        
        return extractability
    
    def _get_selectors_for_element(self, element_type):
        """
        Get CSS selectors for a specific element type.
        
        Args:
            element_type (str): The type of element to get selectors for
            
        Returns:
            list: List of potential CSS selectors
        """
        selectors = []
        
        if element_type == 'title':
            # Check for h1
            h1 = self.soup.find('h1')
            if h1:
                if h1.get('id'):
                    selectors.append(f"h1#{h1.get('id')}")
                elif h1.get('class'):
                    selectors.append(f"h1.{'.'.join(h1.get('class'))}")
                else:
                    selectors.append("h1")
            
            # Check for title classes
            title_elem = self.soup.find(class_=re.compile(r'article-title|post-title|entry-title|headline'))
            if title_elem:
                if title_elem.get('class'):
                    selectors.append(f"{title_elem.name}.{'.'.join(title_elem.get('class'))}")
        
        elif element_type == 'author':
            # Check for author classes
            author_elem = self.soup.find(class_=re.compile(r'author|byline'))
            if author_elem:
                if author_elem.get('class'):
                    selectors.append(f"{author_elem.name}.{'.'.join(author_elem.get('class'))}")
            
            # Check for rel="author"
            rel_author = self.soup.find(rel="author")
            if rel_author:
                selectors.append(f"{rel_author.name}[rel='author']")
        
        elif element_type == 'date':
            # Check for time element
            time_elem = self.soup.find('time')
            if time_elem:
                if time_elem.get('class'):
                    selectors.append(f"time.{'.'.join(time_elem.get('class'))}")
                else:
                    selectors.append("time")
            
            # Check for date classes
            date_elem = self.soup.find(class_=re.compile(r'date|published|posted|time'))
            if date_elem:
                if date_elem.get('class'):
                    selectors.append(f"{date_elem.name}.{'.'.join(date_elem.get('class'))}")
        
        elif element_type == 'section':
            # Check for breadcrumbs
            breadcrumbs = self.soup.find(class_=re.compile(r'breadcrumb'))
            if breadcrumbs:
                if breadcrumbs.get('class'):
                    selectors.append(f"{breadcrumbs.name}.{'.'.join(breadcrumbs.get('class'))}")
        
        return selectors
    
    def get_extraction_recommendations(self):
        """
        Get recommendations for extracting content from this HTML.
        
        Returns:
            dict: Extraction recommendations
        """
        if not self.analysis:
            self.analyze()
        
        recommendations = {
            "url": self.url,
            "domain": self.domain,
            "content_type": self.analysis.get('content_type'),
            "extractability": self.analysis.get('extractability', {}).get('difficulty'),
            "recommendations": {}
        }
        
        # Title recommendations
        title_data = self.analysis.get('metadata', {}).get('title', {})
        if title_data.get('found'):
            recommendations['recommendations']['title'] = {
                "method": "Use meta tags or h1",
                "selectors": title_data.get('selectors', []),
                "example": title_data.get('best_candidate')
            }
        else:
            recommendations['recommendations']['title'] = {
                "method": "Extract from URL or use page title",
                "fallback": "Use document title"
            }
        
        # Author recommendations
        author_data = self.analysis.get('metadata', {}).get('author', {})
        if author_data.get('found'):
            recommendations['recommendations']['author'] = {
                "method": "Use author element or meta tag",
                "selectors": author_data.get('selectors', []),
                "example": author_data.get('best_candidate')
            }
        else:
            recommendations['recommendations']['author'] = {
                "method": "May not be available",
                "fallback": "Use domain name or 'Unknown'"
            }
        
        # Date recommendations
        date_data = self.analysis.get('metadata', {}).get('date', {})
        if date_data.get('found'):
            recommendations['recommendations']['date'] = {
                "method": "Use time element or meta tag",
                "selectors": date_data.get('selectors', []),
                "example": date_data.get('best_candidate')
            }
        else:
            recommendations['recommendations']['date'] = {
                "method": "Use crawl date",
                "fallback": "Extract from URL if possible"
            }
        
        # Content recommendations
        content_data = self.analysis.get('content_structure', {})
        if content_data.get('content_found'):
            recommendations['recommendations']['content'] = {
                "method": "Extract from main content container",
                "selectors": content_data.get('content_selectors', []),
                "paragraph_count": content_data.get('paragraph_count'),
                "word_count": content_data.get('word_count'),
                "notes": []
            }
            
            # Add notes about content
            if content_data.get('has_images'):
                recommendations['recommendations']['content']['notes'].append("Contains images that may need handling")
            if content_data.get('has_blockquotes'):
                recommendations['recommendations']['content']['notes'].append("Contains blockquotes that may need special formatting")
            if content_data.get('has_iframes'):
                recommendations['recommendations']['content']['notes'].append("Contains iframes (possibly embedded content) that may need handling")
        else:
            recommendations['recommendations']['content'] = {
                "method": "Content extraction may be difficult",
                "fallback": "Consider using a full-page extraction library like trafilatura"
            }
        
        return recommendations

def analyze_html_sample(html_content, url=None):
    """
    Analyze a sample of HTML content.
    
    Args:
        html_content (str): The HTML content to analyze
        url (str, optional): The URL the content was fetched from
        
    Returns:
        dict: Analysis results
    """
    analyzer = HTMLAnalyzer(html_content, url)
    analysis = analyzer.analyze()
    recommendations = analyzer.get_extraction_recommendations()
    
    return {
        "analysis": analysis,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    # Example usage
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sample Article - Politics Site</title>
        <meta name="author" content="Jane Doe">
        <meta property="article:published_time" content="2025-04-15T12:00:00Z">
    </head>
    <body>
        <header>
            <nav>
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/politics">Politics</a></li>
                    <li><a href="/opinion">Opinion</a></li>
                </ul>
            </nav>
        </header>
        <main>
            <article class="article-content">
                <h1 class="article-title">This is a Sample Article Title</h1>
                <div class="article-meta">
                    <span class="author">By Jane Doe</span>
                    <time datetime="2025-04-15T12:00:00Z">April 15, 2025</time>
                </div>
                <div class="article-body">
                    <p>This is the first paragraph of the article.</p>
                    <p>This is the second paragraph with some <strong>bold text</strong>.</p>
                    <p>This is the third paragraph with a <a href="#">link</a>.</p>
                    <blockquote>
                        <p>This is a quote from someone important.</p>
                    </blockquote>
                    <p>This is the fourth paragraph after the quote.</p>
                </div>
            </article>
        </main>
        <footer>
            <p>&copy; 2025 Politics Site</p>
        </footer>
    </body>
    </html>
    """
    
    result = analyze_html_sample(sample_html, "https://example.com/politics/sample-article")
    print(json.dumps(result, indent=2))
