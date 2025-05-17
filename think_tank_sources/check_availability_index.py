import gzip
import json
import os
import pandas as pd
import requests
from tqdm import tqdm
from urllib.parse import urlparse
from collections import defaultdict

# List of think tank domains to check
THINK_TANKS = [
    'brookings.edu',
    'csis.org',
    'carnegieendowment.org',
    # 'www.heritage.org',
    # 'www.piie.com',
    # 'www.wilsoncenter.org',
    # 'www.americanprogress.org',
    # 'www.hudson.org',
    # 'www.rand.org',
    # 'www.cfr.org',
    # 'www.atlanticcouncil.org',
    # 'cato.org',
    # 'iiss.org',
    # 'chathamhouse.org',
    # 'sipri.org',
    # 'ifri.org',
    # 'ecfr.eu',
    # 'lowyinstitute.org',
    # 'swp-berlin.org',
    # 'aei.org'
]

def get_surt(domain):
    """Convert domain to SURT format (e.g. edu,brookings)"""
    parts = domain.split('.')
    return ','.join(reversed(parts))

def download_file(url, local_path):
    """Download a file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(local_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=f"Downloading {os.path.basename(local_path)}") as pbar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                pbar.update(len(data))

def check_availability(domain, crawl='CC-MAIN-2025-18'):
    """Check domain availability by downloading and processing CDX files"""
    results = []
    surt = get_surt(domain)
    index_url = f'https://data.commoncrawl.org/crawl-data/{crawl}/cc-index.paths.gz'
    local_index = f'{crawl}_index.paths.gz'
    
    # Download index file if not exists
    if not os.path.exists(local_index):
        download_file(index_url, local_index)
    
    # Find relevant CDX files
    cdx_files = set()
    with gzip.open(local_index, 'rt') as f:
        for line in f:
            if line.startswith('cc-index/collections') and line.endswith('.gz\n'):
                cdx_files.add(f'https://data.commoncrawl.org/{line.strip()}')
    
    # Process each CDX file
    domain_counts = defaultdict(int)
    sample_urls = []
    
    for cdx_url in tqdm(cdx_files, desc=f"Processing {domain}"):
        cdx_file = os.path.basename(cdx_url)
        if not os.path.exists(cdx_file):
            download_file(cdx_url, cdx_file)
        
        with gzip.open(cdx_file, 'rt') as f:
            for line in f:
                if line.startswith(f'{surt})'):
                    domain_counts[domain] += 1
                    if len(sample_urls) < 2:
                        data = json.loads(line.split(' ', 2)[2])
                        sample_urls.append(data['url'])
    
    available = domain_counts[domain] > 0
    results.append({
        'domain': domain,
        'available': available,
        'root_page_count': domain_counts.get(f'{surt})/', 0),
        'total_page_count': domain_counts.get(domain, 0),
        'sample_urls': sample_urls if available else []
    })
    
    return results

def main():
    all_results = []
    
    print(f"Checking availability of {len(THINK_TANKS)} think tanks in CC-MAIN-2025-18...")
    for domain in tqdm(THINK_TANKS):
        all_results.extend(check_availability(domain))
    
    # Create and display results table
    df = pd.DataFrame(all_results)
    print("\nResults:")
    print(df[['domain', 'available', 'root_page_count', 'total_page_count']])
    
    # Save full results to CSV
    df.to_csv('think_tank_availability_index.csv', index=False)
    print("\nFull results saved to think_tank_availability_index.csv")

if __name__ == '__main__':
    main()
