import requests
import gzip
import io
import re
import json
from datetime import datetime
import time

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

def get_cc_news_months(start_year=2016, end_year=2024):
    """Get a list of available months in the CC-NEWS dataset"""
    import requests
    
    try:
        # Try to access the index.html page that lists all available WARC files
        response = requests.get("https://data.commoncrawl.org/crawl-data/CC-NEWS/index.html")
        if response.status_code != 200:
            print(f"Error accessing CC-NEWS index: HTTP {response.status_code}")
            return []
        
        # Extract year links from the index page
        years = re.findall(r'<a href="./(\d{4})/index.html">(\d{4})</a>', response.text)
        
        all_months = []
        for year, _ in years:
            if int(year) < start_year or int(year) > end_year:
                continue
                
            # For each year, get the list of months
            year_response = requests.get(f"https://data.commoncrawl.org/crawl-data/CC-NEWS/{year}/index.html")
            if year_response.status_code == 200:
                # Extract month information from the table
                months = re.findall(r'<th>(\d{2})</th>', year_response.text)
                for month in months:
                    all_months.append((int(year), int(month)))
        
        # Sort by year and month, most recent first
        all_months.sort(reverse=True)
        return all_months
    except Exception as e:
        print(f"Error listing CC-NEWS months: {str(e)}")
        return []

def get_warc_paths_sample(year, month, limit=10):
    """Get a sample of WARC file paths for a specific month"""
    url = f"https://data.commoncrawl.org/crawl-data/CC-NEWS/{year}/{month:02d}/warc.paths.gz"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"No warc.paths.gz found for {year}/{month:02d} (HTTP {response.status_code})")
        return []
    
    # Decompress the gzipped content
    with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
        warc_paths = f.read().decode('utf-8').splitlines()
    
    # Get a sample of WARC paths
    total_warcs = len(warc_paths)
    sample_size = min(limit, total_warcs)
    
    # Take evenly distributed samples
    if sample_size == 1:
        samples = [warc_paths[0]]
    else:
        step = total_warcs // sample_size
        samples = [warc_paths[i * step] for i in range(sample_size)]
    
    return samples, total_warcs

def extract_cdx_from_warc_path(warc_path):
    """Extract CDX information from a WARC path"""
    # Example WARC path: crawl-data/CC-NEWS/2024/01/CC-NEWS-20240101002957-01499.warc.gz
    # We need to extract the date and sequence number
    match = re.search(r'CC-NEWS-(\d{14})-(\d{5})\.warc\.gz', warc_path)
    if match:
        date = match.group(1)
        seq = match.group(2)
        return date, seq
    return None, None

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

def check_publisher_in_month(year, month, publisher, sample_size=10):
    """Check if a publisher's content exists in a specific month"""
    print(f"Checking {publisher['name']} in {year}/{month:02d}...")
    
    # Get a sample of WARC paths for this month
    warc_paths, total_warcs = get_warc_paths_sample(year, month, limit=sample_size)
    
    if not warc_paths:
        print(f"No WARC files found for {year}/{month:02d}")
        return {
            "available": False,
            "message": f"No WARC files found for {year}/{month:02d}"
        }
    
    print(f"Found {total_warcs} WARC files for {year}/{month:02d}, checking {len(warc_paths)} samples")
    
    # Check each WARC file for the publisher's domain
    found_urls = []
    
    for warc_path in warc_paths:
        print(f"Checking {warc_path}...")
        
        # Extract the CDX information from the WARC path
        date, seq = extract_cdx_from_warc_path(warc_path)
        if not date or not seq:
            print(f"Could not extract CDX information from {warc_path}")
            continue
        
        # We can't directly query the CDX API for CC-NEWS
        # Instead, we'll check the WARC file's index
        index_url = f"https://data.commoncrawl.org/crawl-data/CC-NEWS/{year}/{month:02d}/cdx-{date}-{seq}.gz"
        
        try:
            # Try to access the CDX index file
            response = requests.get(index_url)
            if response.status_code != 200:
                # If the CDX index file doesn't exist, skip this WARC file
                print(f"No CDX index found for {warc_path} (HTTP {response.status_code})")
                continue
            
            # Decompress the gzipped content
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                cdx_lines = f.read().decode('utf-8').splitlines()
            
            # Check each CDX line for the publisher's domain
            for line in cdx_lines:
                try:
                    # CDX line format: urlkey timestamp original status mime digest length offset filename
                    parts = line.split(' ')
                    if len(parts) < 3:
                        continue
                    
                    url = parts[2]  # original URL
                    
                    if check_url_for_publisher(url, publisher):
                        found_urls.append({
                            "url": url,
                            "warc_path": warc_path
                        })
                except Exception as e:
                    print(f"Error parsing CDX line: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error checking CDX index for {warc_path}: {str(e)}")
            continue
    
    if found_urls:
        return {
            "available": True,
            "message": f"Found {len(found_urls)} {publisher['name']} politics URLs in {year}/{month:02d}",
            "urls": found_urls
        }
    else:
        return {
            "available": False,
            "message": f"No {publisher['name']} politics URLs found in {year}/{month:02d} samples"
        }

def main():
    # Get available months
    print("Getting available months in CC-NEWS dataset...")
    months = get_cc_news_months(start_year=2016, end_year=2024)
    
    if not months:
        print("No months found in CC-NEWS dataset")
        return
    
    print(f"Found {len(months)} months in CC-NEWS dataset")
    print(f"Most recent: {months[0][0]}/{months[0][1]:02d}")
    print(f"Oldest: {months[-1][0]}/{months[-1][1]:02d}")
    
    # Sort months chronologically (oldest first)
    months.sort()
    
    # Check each publisher starting from 2020 and moving forward
    results = {}
    
    for publisher in PUBLISHERS:
        publisher_name = publisher["name"]
        results[publisher_name] = []
        
        print(f"\nChecking {publisher_name}...")
        
        # Track the last year/month where content was found
        last_available_year = None
        last_available_month = None
        
        # Check every 6 months to find the cutoff more efficiently
        check_months = []
        for year in range(2016, 2025):
            for month in [1, 7]:  # January and July of each year
                if (year, month) in months:
                    check_months.append((year, month))
        
        # Add the most recent month to ensure we check the latest data
        if months[-1] not in check_months:
            check_months.append(months[-1])
        
        # Sort chronologically
        check_months.sort()
        
        print(f"Checking {len(check_months)} sample months for {publisher_name}...")
        
        for year, month in check_months:
            print(f"Checking {year}/{month:02d}...")
            result = check_publisher_in_month(year, month, publisher, sample_size=3)
            result["year"] = year
            result["month"] = month
            results[publisher_name].append(result)
            
            if result["available"]:
                last_available_year = year
                last_available_month = month
                print(f"Found {publisher_name} politics URLs in {year}/{month:02d}")
            
            # Sleep to avoid rate limiting
            time.sleep(1)
        
        # If we found content, report the cutoff
        if last_available_year:
            print(f"{publisher_name} content last found in {last_available_year}/{last_available_month:02d}")
        else:
            print(f"No {publisher_name} content found in any checked months")
    
    # Save results to JSON file
    with open("cc_news_publisher_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n=== SUMMARY ===")
    for publisher_name, publisher_results in results.items():
        available_months = []
        for result in publisher_results:
            if result["available"]:
                available_months.append(f"{result['year']}/{result['month']:02d}")
        
        if available_months:
            print(f"{publisher_name}: Available in {', '.join(available_months)}")
        else:
            print(f"{publisher_name}: Not found in checked months")
    
    print("\nDetailed results saved to cc_news_publisher_results.json")

if __name__ == "__main__":
    main()
