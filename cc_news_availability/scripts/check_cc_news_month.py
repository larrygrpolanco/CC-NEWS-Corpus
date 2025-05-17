import requests
import gzip
import io
import sys

def check_cc_news_month(year, month):
    """Check if WARC files are available for a specific month in the CC-NEWS dataset"""
    print(f"Checking CC-NEWS for {year}/{month:02d}...")
    
    try:
        # Check if the warc.paths.gz file exists for this month
        url = f"https://data.commoncrawl.org/crawl-data/CC-NEWS/{year}/{month:02d}/warc.paths.gz"
        print(f"Requesting {url}...")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"No warc.paths.gz found for {year}/{month:02d} (HTTP {response.status_code})")
            return False
        
        print(f"Found warc.paths.gz for {year}/{month:02d}")
        
        # Decompress the gzipped content
        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
            warc_paths = f.read().decode('utf-8').splitlines()
        
        if not warc_paths:
            print(f"No WARC files found for {year}/{month:02d}")
            return False
        
        print(f"Found {len(warc_paths)} WARC files for {year}/{month:02d}")
        
        # Print the first 5 WARC files
        print("Sample WARC files:")
        for i, path in enumerate(warc_paths[:5]):
            print(f"  {i+1}. {path}")
        
        return True
        
    except Exception as e:
        print(f"Error checking {year}/{month:02d}: {str(e)}")
        return False

if __name__ == "__main__":
    # Check the most recent months
    for year in [2024, 2023]:
        for month in range(1, 13):
            if check_cc_news_month(year, month):
                print(f"Successfully found WARC files for {year}/{month:02d}")
                print()
            else:
                print(f"No WARC files found for {year}/{month:02d}")
                print()
            
            # Only check the first month that has WARC files
            if year == 2024 and month == 1:
                sys.exit(0)
