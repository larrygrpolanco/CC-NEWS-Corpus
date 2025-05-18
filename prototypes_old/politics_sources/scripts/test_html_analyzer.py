#!/usr/bin/env python3
"""
Test script for the HTML analyzer utilities.
This script tests the basic functionality of the html_analyzer.py module.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the utils modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.html_analyzer import HTMLAnalyzer, analyze_html_sample

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample HTML for testing
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Article - Politics Site</title>
    <meta name="author" content="Jane Doe">
    <meta property="article:published_time" content="2025-04-15T12:00:00Z">
    <meta property="og:title" content="This is a Sample Article Title">
    <meta property="article:section" content="Politics">
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
                <ul>
                    <li>This is a list item</li>
                    <li>This is another list item</li>
                </ul>
                <p>This is the fifth paragraph after the list.</p>
            </div>
        </article>
    </main>
    <footer>
        <p>&copy; 2025 Politics Site</p>
    </footer>
</body>
</html>
"""

def test_html_analyzer(html_content, url=None):
    """
    Test the HTMLAnalyzer class.
    
    Args:
        html_content (str): The HTML content to analyze
        url (str, optional): The URL the content was fetched from
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Testing HTMLAnalyzer")
    
    try:
        # Create an HTMLAnalyzer instance
        analyzer = HTMLAnalyzer(html_content, url)
        
        # Analyze the HTML
        analysis = analyzer.analyze()
        
        logger.info("Analysis results:")
        logger.info(f"Content type: {analysis['content_type']}")
        logger.info(f"Metadata found: {json.dumps(analysis['metadata'], indent=2)}")
        logger.info(f"Content structure: {json.dumps(analysis['content_structure'], indent=2)}")
        logger.info(f"Extractability: {json.dumps(analysis['extractability'], indent=2)}")
        
        # Get extraction recommendations
        recommendations = analyzer.get_extraction_recommendations()
        
        logger.info("Extraction recommendations:")
        logger.info(json.dumps(recommendations, indent=2))
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing HTMLAnalyzer: {e}")
        return False

def test_analyze_html_sample(html_content, url=None):
    """
    Test the analyze_html_sample function.
    
    Args:
        html_content (str): The HTML content to analyze
        url (str, optional): The URL the content was fetched from
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Testing analyze_html_sample")
    
    try:
        # Analyze the HTML sample
        result = analyze_html_sample(html_content, url)
        
        logger.info("Analysis results:")
        logger.info(json.dumps(result, indent=2))
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing analyze_html_sample: {e}")
        return False

def test_with_file(file_path, url=None):
    """
    Test the HTML analyzer with a file.
    
    Args:
        file_path (str): Path to the HTML file
        url (str, optional): The URL the content was fetched from
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Testing with file: {file_path}")
    
    try:
        # Read the HTML file
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Test the HTMLAnalyzer
        success1 = test_html_analyzer(html_content, url)
        
        # Test the analyze_html_sample function
        success2 = test_analyze_html_sample(html_content, url)
        
        return success1 and success2
    
    except Exception as e:
        logger.error(f"Error testing with file: {e}")
        return False

def main():
    """
    Main function to run the tests.
    """
    parser = argparse.ArgumentParser(description='Test HTML analyzer utilities')
    parser.add_argument('--file', type=str, default=None,
                        help='Path to an HTML file to analyze (optional)')
    parser.add_argument('--url', type=str, default='https://example.com/politics/sample-article',
                        help='URL to associate with the HTML content (default: https://example.com/politics/sample-article)')
    parser.add_argument('--save-sample', action='store_true',
                        help='Save the sample HTML to a file')
    args = parser.parse_args()
    
    # Save the sample HTML to a file if requested
    if args.save_sample:
        sample_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  'data', 'sample_content', 'sample_article.html')
        os.makedirs(os.path.dirname(sample_path), exist_ok=True)
        
        with open(sample_path, 'w', encoding='utf-8') as f:
            f.write(SAMPLE_HTML)
        
        logger.info(f"Saved sample HTML to {sample_path}")
    
    # Test with a file if provided
    if args.file:
        success = test_with_file(args.file, args.url)
        logger.info(f"File test {'succeeded' if success else 'failed'}")
    else:
        # Test with the sample HTML
        logger.info("Testing with sample HTML")
        
        # Test the HTMLAnalyzer
        success1 = test_html_analyzer(SAMPLE_HTML, args.url)
        logger.info(f"HTMLAnalyzer test {'succeeded' if success1 else 'failed'}")
        
        # Test the analyze_html_sample function
        success2 = test_analyze_html_sample(SAMPLE_HTML, args.url)
        logger.info(f"analyze_html_sample test {'succeeded' if success2 else 'failed'}")
    
    logger.info("Testing complete")

if __name__ == "__main__":
    main()
