import requests
import tempfile
import os
from warcio.archiveiterator import ArchiveIterator

def download_warc_sample(warc_path, max_size_mb=10):
    """Download a sample of a WARC file (first N MB)"""
    url = f"https://data.commoncrawl.org/{warc_path}"
    print(f"Downloading sample of {url} (max {max_size_mb} MB)...")
    
    # Convert MB to bytes
    max_size = max_size_mb * 1024 * 1024
    
    # Use a range request to get only the first part of the file
    headers = {'Range': f'bytes=0-{max_size}'}
    response = requests.get(url, headers=headers, stream=True)
    
    if response.status_code not in [200, 206]:  # 200 OK or 206 Partial Content
        print(f"Error downloading WARC sample: HTTP {response.status_code}")
        return None
    
    # Save the WARC sample to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.warc.gz') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
        
        return f.name

def process_warc_sample(warc_file):
    """Process a WARC file sample and look for publisher URLs"""
    # Target publishers
    target_publishers = [
        {"name": "Wall Street Journal", "domain": "wsj.com"},
        {"name": "New York Times", "domain": "nytimes.com"},
        {"name": "Washington Post", "domain": "washingtonpost.com"},
        {"name": "USA Today", "domain": "usatoday.com"}
    ]
    
    # Initialize results for target publishers
    results = {publisher["name"]: [] for publisher in target_publishers}
    
    # Also track all domains to see what's available
    all_domains = {}
    
    print(f"Processing {warc_file}...")
    
    try:
        with open(warc_file, 'rb') as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type == 'response':
                    url = record.rec_headers.get_header('WARC-Target-URI')
                    
                    # Check for target publishers
                    for publisher in target_publishers:
                        if publisher["domain"] in url:
                            results[publisher["name"]].append({
                                "url": url,
                                "content_type": record.http_headers.get_header('Content-Type'),
                                "status": record.http_headers.get_header('Status')
                            })
                    
                    # Extract domain from URL
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        
                        # Only track domains that might be news sources
                        news_keywords = ['news', 'times', 'post', 'tribune', 'herald', 'journal', 'gazette', 'daily', 'press']
                        if any(keyword in domain for keyword in news_keywords) or domain.endswith('.news'):
                            if domain in all_domains:
                                all_domains[domain] += 1
                            else:
                                all_domains[domain] = 1
                    except:
                        pass
    except Exception as e:
        print(f"Error processing WARC file: {str(e)}")
    
    # Add all domains to results
    results["all_news_domains"] = all_domains
    
    return results

def main():
    # Try WARC files from different years
    warc_paths = [
        # 2018
        "crawl-data/CC-NEWS/2018/01/CC-NEWS-20180101065221-00039.warc.gz",
        # 2020
        "crawl-data/CC-NEWS/2020/01/CC-NEWS-20200101023937-00188.warc.gz",
        # 2022
        "crawl-data/CC-NEWS/2022/01/CC-NEWS-20220101003215-00343.warc.gz",
        # 2024 (most recent)
        "crawl-data/CC-NEWS/2024/01/CC-NEWS-20240101002957-01499.warc.gz"
    ]
    
    all_results = {
        "Wall Street Journal": [],
        "New York Times": [],
        "Washington Post": [],
        "USA Today": []
    }
    
    all_domains = {}
    
    for warc_path in warc_paths:
        print(f"\nChecking {warc_path}...")
        
        # Download a sample of the WARC file
        warc_file = download_warc_sample(warc_path)
        
        if not warc_file:
            print("Failed to download WARC sample")
            continue
        
        # Process the WARC file
        results = process_warc_sample(warc_file)
        
        # Add results to overall results
        for publisher_name, urls in results.items():
            if publisher_name == "all_news_domains":
                # Merge domain counts
                for domain, count in urls.items():
                    if domain in all_domains:
                        all_domains[domain] += count
                    else:
                        all_domains[domain] = count
            else:
                all_results[publisher_name].extend(urls)
        
        # Delete the temporary file
        os.unlink(warc_file)
    
    # Print the overall results
    print("\n=== OVERALL RESULTS ===")
    for publisher_name, urls in all_results.items():
        if urls:
            print(f"\n{publisher_name}: Found {len(urls)} URLs")
            for i, url_info in enumerate(urls[:10]):  # Print the first 10 URLs
                print(f"  {i+1}. {url_info['url']}")
                print(f"     Content-Type: {url_info['content_type']}")
                print(f"     Status: {url_info['status']}")
        else:
            print(f"\n{publisher_name}: No URLs found")
    
    # Print the top news domains found
    print("\n=== TOP NEWS DOMAINS FOUND ===")
    sorted_domains = sorted(all_domains.items(), key=lambda x: x[1], reverse=True)
    for i, (domain, count) in enumerate(sorted_domains[:20]):  # Print the top 20 domains
        print(f"  {i+1}. {domain}: {count} occurrences")

if __name__ == "__main__":
    main()
