import requests
import re
import time
from datetime import datetime, timedelta

def get_cc_news_warc_list(year, month):
    """Get a list of WARC files for a specific year and month in the CC-NEWS dataset."""
    url = f"https://data.commoncrawl.org/crawl-data/CC-NEWS/{year}/{month:02d}/"
    response = requests.get(url)
    
    if response.status_code == 200:
        # Extract WARC filenames using regex
        warc_files = re.findall(r'CC-NEWS-[0-9]{14}-[0-9]{5}\.warc\.gz', response.text)
        return warc_files
    else:
        print(f"Error fetching WARC list: {response.status_code} - {response.text}")
        return []

def check_recent_months():
    """Check the most recent months for CC-NEWS WARC files."""
    results = []
    
    # Check specific years and months
    years_months = [
        (2024, 12), (2024, 11), (2024, 10), (2024, 9),
        (2024, 8), (2024, 7), (2024, 6), (2024, 5),
        (2024, 4), (2024, 3), (2024, 2), (2024, 1),
        (2023, 12), (2023, 11), (2023, 10)
    ]
    
    for year, month in years_months:
        
        print(f"Checking CC-NEWS for {year}/{month:02d}...")
        warc_files = get_cc_news_warc_list(year, month)
        
        if warc_files:
            print(f"Found {len(warc_files)} WARC files for {year}/{month:02d}")
            # Get the first and last file to show the date range
            first_file = warc_files[0]
            last_file = warc_files[-1]
            first_date = first_file.split('-')[2][:8]  # Extract YYYYMMDD from filename
            last_date = last_file.split('-')[2][:8]
            
            results.append({
                'year': year,
                'month': month,
                'warc_count': len(warc_files),
                'first_file': first_file,
                'last_file': last_file,
                'date_range': f"{first_date} to {last_date}"
            })
        else:
            print(f"No WARC files found for {year}/{month:02d}")
        
        time.sleep(1)  # Sleep to avoid rate limiting
    
    return results

# Run the check
results = check_recent_months()

# Print results
print("\nSummary of CC-NEWS WARC files:")
for result in results:
    print(f"{result['year']}/{result['month']:02d}: {result['warc_count']} files, {result['date_range']}")
    print(f"  First file: {result['first_file']}")
    print(f"  Last file: {result['last_file']}")
