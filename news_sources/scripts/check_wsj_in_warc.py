import requests
import gzip
import io
import re
import sys
import tempfile
import os
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup

# Publisher configurations
PUBLISHERS = [
    {
        "name": "Wall Street Journal",
        "domain": "wsj.com",
        "politics_patterns": [
            r"wsj\.com/politics",
            r"wsj\.com/politics/elections",
            r"wsj\.com/politics/national-security",
            r"wsj\.com/politics/policy"
        ]
    },
    {
        "name": "New York Times",
        "domain": "nytimes.com",
        "politics_patterns": [
            r"nytimes\.com/\d{4}/\d{2}/\d{2}/us/politics/",
            r"nytimes\.com/section/politics"
        ]
    },
    {
        "name": "Washington Post",
        "domain": "washingtonpost.com",
        "politics_patterns": [
            r"washingtonpost\.com/politics/\d{4}/\d{2}/\d{2}"
        ]
    },
    {
        "name": "USA Today",
        "domain": "usatoday.com",
        "politics_patterns": [
            r"usatoday\.com/news/politics",
            r"usatoday\.com/story/news/politics"
        ]
    }
]

def get_warc_paths(year, month, limit=5):
    """Get a list of WARC file paths for a specific month"""
    url = f"https://data.commoncrawl.org/crawl-data/CC-NEWS/{year}/{month:02d}/warc.paths.gz"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"No warc.paths.gz found for {year}/{month:02d} (HTTP {response.status_code})")
        return []
    
    # Decompress the gzipped content
    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
        warc_paths = f.read().decode('utf-8').splitlines()
    
    # Return the first 'limit' paths
    return warc_paths[:limit]

def download_warc_file(warc_path):
    """Download a WARC file from Common Crawl"""
    url = f"https://data.commoncrawl.org/{warc_path}"
    print(f"Downloading {url}...")
    
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        print(f"Error downloading WARC file: HTTP {response.status_code}")
        return None
    
    # Save the WARC file to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.warc.gz') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
        
        return f.name

def check_url_for_publisher(url, publisher):
    """Check if a URL matches a publisher's domain and politics patterns"""
    # Check if the URL contains the publisher's domain
    if publisher["domain"] not in url:
        return False
    
    # Check if the URL matches any of the publisher's politics patterns
    for pattern in publisher["politics_patterns"]:
        if re.search(pattern, url):
            return True
    
    return False

def process_warc_file(warc_file, publishers):
    """Process a WARC file and look for publisher URLs"""
    results = {publisher["name"]: [] for publisher in publishers}
    
    print(f"Processing {warc_file}...")
    
    try:
        with open(warc_file, 'rb') as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
                    url = record.rec_headers.get_header('WARC-Target-URI')
                    
                    for publisher in publishers:
                        if check_url_for_publisher(url, publisher):
                            # Extract the title from the HTML content
                            content = record.content_stream().read()
                            try:
                                soup = BeautifulSoup(content, 'html.parser')
                                title = soup.title.string if soup.title else "No title"
                            except:
                                title = "Error parsing HTML"
                            
                            results[publisher["name"]].append({
                                "url": url,
                                "title": title
                            })
    except Exception as e:
        print(f"Error processing WARC file: {str(e)}")
    
    return results

def main():
    # Check January 2024 for WSJ politics URLs
    year = 2024
    month = 1
    
    print(f"Checking CC-NEWS for {year}/{month:02d}...")
    
    # Get a list of WARC file paths
    warc_paths = get_warc_paths(year, month, limit=3)
    
    if not warc_paths:
        print(f"No WARC files found for {year}/{month:02d}")
        return
    
    print(f"Found {len(warc_paths)} WARC files for {year}/{month:02d}")
    
    # Process each WARC file
    all_results = {publisher["name"]: [] for publisher in PUBLISHERS}
    
    for warc_path in warc_paths:
        # Download the WARC file
        warc_file = download_warc_file(warc_path)
        
        if not warc_file:
            print(f"Error downloading {warc_path}")
            continue
        
        # Process the WARC file
        results = process_warc_file(warc_file, PUBLISHERS)
        
        # Add the results to the overall results
        for publisher_name, urls in results.items():
            all_results[publisher_name].extend(urls)
        
        # Delete the temporary file
        os.unlink(warc_file)
    
    # Print the results
    print("\n=== RESULTS ===")
    for publisher_name, urls in all_results.items():
        if urls:
            print(f"\n{publisher_name}: Found {len(urls)} politics URLs")
            for i, url_info in enumerate(urls[:10]):  # Print the first 10 URLs
                print(f"  {i+1}. {url_info['url']}")
                print(f"     Title: {url_info['title']}")
        else:
            print(f"\n{publisher_name}: No politics URLs found")

if __name__ == "__main__":
    main()
