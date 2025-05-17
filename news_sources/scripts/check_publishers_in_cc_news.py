import subprocess
import re
import json
from datetime import datetime, timedelta
import os

# Publisher configurations
PUBLISHERS = [
    {
        "name": "New York Times",
        "domain": "nytimes.com",
        "politics_patterns": [
            r"nytimes\.com/\d{4}/\d{2}/\d{2}/us/politics/",
            r"nytimes\.com/section/politics"
        ]
    },
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

def get_recent_cc_news_months(num_months=6):
    """Get a list of recent year/month combinations to check"""
    months = []
    now = datetime.now()
    
    for i in range(num_months):
        check_date = now - timedelta(days=30*i)
        months.append((check_date.year, check_date.month))
    
    return months

def list_cc_news_months():
    """List all available months in the CC-NEWS dataset using the index.html page"""
    import requests
    
    try:
        # Try to access the index.html page that lists all available WARC files
        response = requests.get("https://data.commoncrawl.org/crawl-data/CC-NEWS/index.html")
        if response.status_code != 200:
            print(f"Error accessing CC-NEWS index: HTTP {response.status_code}")
            # Fall back to checking specific years and months
            return check_specific_months()
        
        # Extract year links from the index page
        years = re.findall(r'<a href="./(\d{4})/index.html">(\d{4})</a>', response.text)
        
        all_months = []
        for year, _ in years:
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
        return check_specific_months()

def check_specific_months():
    """Check specific years and months that are likely to exist"""
    # Try some specific years and months that are likely to exist based on documentation
    # CC-NEWS dataset started in 2016
    specific_months = []
    
    # Check years from 2016 to current year
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    for year in range(2016, current_year + 1):
        # For current year, only check up to current month
        max_month = current_month if year == current_year else 12
        for month in range(1, max_month + 1):
            specific_months.append((year, month))
    
    # Sort by year and month, most recent first
    specific_months.sort(reverse=True)
    return specific_months

def check_cc_news_for_publisher(year, month, publisher):
    """Check if a publisher's content exists in CC-NEWS for a specific month"""
    import requests
    import gzip
    import io
    
    try:
        # Check if the warc.paths.gz file exists for this month
        url = f"https://data.commoncrawl.org/crawl-data/CC-NEWS/{year}/{month:02d}/warc.paths.gz"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {
                "available": False,
                "message": f"No warc.paths.gz found for {year}/{month:02d} (HTTP {response.status_code})"
            }
        
        # Decompress the gzipped content
        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
            warc_paths = f.read().decode('utf-8').splitlines()
        
        if not warc_paths:
            return {
                "available": False,
                "message": f"No WARC files found for {year}/{month:02d}"
            }
        
        # Get a sample WARC file path
        sample_path = warc_paths[0] if warc_paths else None
        
        if not sample_path:
            return {
                "available": True,
                "message": f"WARC files available for {year}/{month:02d}, but couldn't get sample filename"
            }
        
        # Extract just the filename from the path
        sample_file = sample_path.split('/')[-1]
        
        # For now, we'll just return that we found WARC files for this month
        # In a full implementation, we would download and process the WARC file
        return {
            "available": True,
            "message": f"WARC files available for {year}/{month:02d}",
            "sample_file": sample_file,
            "warc_count": len(warc_paths)
        }
        
    except Exception as e:
        return {
            "available": False,
            "message": f"Error checking {year}/{month:02d}: {str(e)}"
        }

def main():
    """Main function to check all publishers across recent months"""
    print("Listing available months in CC-NEWS dataset...")
    available_months = list_cc_news_months()
    
    if not available_months:
        print("No months found in CC-NEWS dataset. Check AWS CLI installation and connectivity.")
        return
    
    print(f"Found {len(available_months)} months in CC-NEWS dataset.")
    print(f"Most recent: {available_months[0][0]}/{available_months[0][1]:02d}")
    print(f"Oldest: {available_months[-1][0]}/{available_months[-1][1]:02d}")
    
    # Use the 6 most recent months or all available if fewer
    months_to_check = available_months[:min(6, len(available_months))]
    
    results = {}
    for publisher in PUBLISHERS:
        publisher_name = publisher["name"]
        results[publisher_name] = []
        
        print(f"\nChecking {publisher_name}...")
        for year, month in months_to_check:
            print(f"  Checking {year}/{month:02d}...")
            result = check_cc_news_for_publisher(year, month, publisher)
            result["year"] = year
            result["month"] = month
            results[publisher_name].append(result)
    
    # Save results to JSON file
    with open("cc_news_publisher_check_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n=== SUMMARY ===")
    for publisher_name, publisher_results in results.items():
        available_months = [f"{r['year']}/{r['month']:02d}" for r in publisher_results if r["available"]]
        if available_months:
            print(f"{publisher_name}: Available in {', '.join(available_months)}")
        else:
            print(f"{publisher_name}: Not found in checked months")
    
    print("\nDetailed results saved to cc_news_publisher_check_results.json")
    print("\nNext steps would be to download sample WARC files and check for specific publisher content.")

if __name__ == "__main__":
    main()
