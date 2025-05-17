"""
Common Crawl API utilities for checking source availability and fetching content.
"""

import requests
import json
import time
import random
from urllib.parse import quote
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
CDX_API_BASE = "https://index.commoncrawl.org/"
DATA_BASE_URL = "https://data.commoncrawl.org/"
USER_AGENT = "politics-sources-checker/1.0 (Research project analyzing political content availability)"

# Default crawls to check (most recent first)
DEFAULT_CRAWLS = [
    "CC-MAIN-2025-18",  # April 2025
    "CC-MAIN-2025-13",  # March 2025
    "CC-MAIN-2025-08",  # February 2025
    "CC-MAIN-2025-04",  # January 2025
]

def query_cdx_api(url, crawl_id, params=None, max_retries=3, retry_delay=2):
    """
    Query the Common Crawl CDX API for a specific URL in a specific crawl.
    
    Args:
        url (str): The URL to query for
        crawl_id (str): The ID of the crawl to query (e.g., "CC-MAIN-2025-18")
        params (dict, optional): Additional query parameters
        max_retries (int, optional): Maximum number of retries on failure
        retry_delay (int, optional): Delay between retries in seconds
        
    Returns:
        list: List of records matching the query, or None if an error occurred
    """
    if params is None:
        params = {}
    
    # Ensure URL is properly encoded
    encoded_url = quote(url)
    
    # Construct the API URL
    api_url = f"{CDX_API_BASE}{crawl_id}-index"
    
    # Set default parameters
    default_params = {
        "url": encoded_url,
        "output": "json",
    }
    
    # Merge default parameters with any additional parameters
    query_params = {**default_params, **params}
    
    # Set headers
    headers = {
        "User-Agent": USER_AGENT
    }
    
    # Try the request with retries
    for attempt in range(max_retries):
        try:
            logger.info(f"Querying CDX API for {url} in {crawl_id} (attempt {attempt+1}/{max_retries})")
            response = requests.get(api_url, params=query_params, headers=headers)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the response
                if response.text.strip():
                    records = []
                    for line in response.text.strip().split('\n'):
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse JSON from line: {line}")
                    return records
                else:
                    logger.info(f"No records found for {url} in {crawl_id}")
                    return []
            elif response.status_code == 429 or response.status_code >= 500:
                # Rate limiting or server error, retry after delay
                logger.warning(f"Received status code {response.status_code}, retrying in {retry_delay} seconds")
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                # Other error
                logger.error(f"Error querying CDX API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
            else:
                return None
    
    # If we get here, all retries failed
    logger.error(f"All retries failed for {url} in {crawl_id}")
    return None

def check_domain_availability(domain, crawl_id):
    """
    Check if a domain is available in a specific crawl.
    
    Args:
        domain (str): The domain to check (e.g., "example.com")
        crawl_id (str): The ID of the crawl to check (e.g., "CC-MAIN-2025-18")
        
    Returns:
        dict: Dictionary with availability information
    """
    # Ensure domain doesn't have protocol
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://', 1)[1]
    
    # Remove trailing slash if present
    if domain.endswith('/'):
        domain = domain[:-1]
    
    # Query for the domain
    records = query_cdx_api(domain, crawl_id)
    
    # Check if we got any records
    if records is None:
        return {
            "domain": domain,
            "crawl_id": crawl_id,
            "available": False,
            "error": True,
            "page_count": 0,
            "has_articles": False,
            "sample_urls": []
        }
    
    # Check if we have any records
    if not records:
        return {
            "domain": domain,
            "crawl_id": crawl_id,
            "available": False,
            "error": False,
            "page_count": 0,
            "has_articles": False,
            "sample_urls": []
        }
    
    # Get a count of pages
    page_count = len(records)
    
    # Check if we have any article-like pages
    # This is a simple heuristic - we look for URLs that might be articles
    article_indicators = [
        '/article/', '/articles/', '/story/', '/stories/', 
        '/news/', '/opinion/', '/blog/', '/blogs/',
        '/analysis/', '/commentary/', '/report/', '/reports/',
        '/publication/', '/publications/', '/research/',
        '/post/', '/posts/', '/view/', '/read/'
    ]
    
    article_urls = []
    for record in records:
        url = record.get('url', '')
        for indicator in article_indicators:
            if indicator in url.lower():
                article_urls.append(url)
                break
    
    # Get a sample of URLs (up to 5)
    sample_urls = random.sample(article_urls, min(5, len(article_urls))) if article_urls else []
    
    return {
        "domain": domain,
        "crawl_id": crawl_id,
        "available": True,
        "error": False,
        "page_count": page_count,
        "has_articles": len(article_urls) > 0,
        "article_count": len(article_urls),
        "sample_urls": sample_urls
    }

def check_domain_in_multiple_crawls(domain, crawl_ids=None):
    """
    Check a domain's availability across multiple crawls.
    
    Args:
        domain (str): The domain to check
        crawl_ids (list, optional): List of crawl IDs to check. If None, uses DEFAULT_CRAWLS.
        
    Returns:
        dict: Dictionary with availability information for each crawl
    """
    if crawl_ids is None:
        crawl_ids = DEFAULT_CRAWLS
    
    results = {}
    
    for crawl_id in crawl_ids:
        # Add a small delay between requests to be polite to the API
        time.sleep(1)
        
        # Check availability in this crawl
        availability = check_domain_availability(domain, crawl_id)
        
        # Add to results
        results[crawl_id] = availability
    
    return {
        "domain": domain,
        "results": results
    }

def fetch_warc_record(filename, offset, length):
    """
    Fetch a specific WARC record from Common Crawl.
    
    Args:
        filename (str): The path to the WARC file
        offset (int): The offset of the record within the WARC file
        length (int): The length of the record
        
    Returns:
        bytes: The raw content of the WARC record, or None if an error occurred
    """
    # Construct the URL
    url = f"{DATA_BASE_URL}{filename}"
    
    # Set headers
    headers = {
        "User-Agent": USER_AGENT,
        "Range": f"bytes={offset}-{offset+length-1}"
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers, stream=True)
        
        # Check if the request was successful
        if response.status_code == 206:  # Partial Content
            return response.content
        else:
            logger.error(f"Error fetching WARC record: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
        return None

def get_sample_articles(domain, crawl_id, count=5):
    """
    Get sample article URLs from a domain in a specific crawl.
    
    Args:
        domain (str): The domain to get samples from
        crawl_id (str): The ID of the crawl to query
        count (int, optional): Number of sample articles to get
        
    Returns:
        list: List of dictionaries with article information
    """
    # Ensure domain doesn't have protocol
    if domain.startswith(('http://', 'https://')):
        domain = domain.split('://', 1)[1]
    
    # Remove trailing slash if present
    if domain.endswith('/'):
        domain = domain[:-1]
    
    # Article indicators in URL
    article_indicators = [
        '/article/', '/articles/', '/story/', '/stories/', 
        '/news/', '/opinion/', '/blog/', '/blogs/',
        '/analysis/', '/commentary/', '/report/', '/reports/',
        '/publication/', '/publications/', '/research/',
        '/post/', '/posts/', '/view/', '/read/'
    ]
    
    # Query for the domain with wildcard
    records = query_cdx_api(f"{domain}/*", crawl_id)
    
    if not records:
        return []
    
    # Filter for likely article URLs
    article_records = []
    for record in records:
        url = record.get('url', '')
        for indicator in article_indicators:
            if indicator in url.lower():
                article_records.append(record)
                break
    
    # If we don't have enough article records, use any records
    if len(article_records) < count:
        article_records = records
    
    # Get a random sample
    if len(article_records) > count:
        sample_records = random.sample(article_records, count)
    else:
        sample_records = article_records
    
    # Extract relevant information
    samples = []
    for record in sample_records:
        samples.append({
            "url": record.get('url'),
            "timestamp": record.get('timestamp'),
            "mime": record.get('mime'),
            "status": record.get('status'),
            "digest": record.get('digest'),
            "filename": record.get('filename'),
            "offset": record.get('offset'),
            "length": record.get('length')
        })
    
    return samples

if __name__ == "__main__":
    # Example usage
    print("Testing CDX API utilities...")
    
    # Test domain availability check
    domain = "brookings.edu"
    crawl_id = "CC-MAIN-2025-18"
    
    print(f"Checking availability of {domain} in {crawl_id}...")
    availability = check_domain_availability(domain, crawl_id)
    print(json.dumps(availability, indent=2))
    
    # Test multi-crawl check
    print(f"Checking {domain} across multiple crawls...")
    multi_results = check_domain_in_multiple_crawls(domain, DEFAULT_CRAWLS[:2])
    print(json.dumps(multi_results, indent=2))
