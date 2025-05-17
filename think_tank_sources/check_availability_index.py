import requests
import pandas as pd
from tqdm import tqdm
import os
import gzip
import json
from collections import defaultdict

def get_latest_crawl():
    """Get the latest Common Crawl ID"""
    try:
        response = requests.get('http://index.commoncrawl.org/collinfo.json')
        response.raise_for_status()
        return response.json()[0]['id']
    except Exception:
        return 'CC-MAIN-2024-22'

def get_surt(domain):
    """Convert domain to SURT format"""
    parts = domain.split('.')
    return ','.join(reversed(parts))

def download_file(url, local_path):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(local_path, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, 
                 desc=f"Downloading {os.path.basename(local_path)}") as pbar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                pbar.update(len(data))

def check_availability(domain, crawl):
    """Check domain availability in CDX files"""
    results = []
    surt = get_surt(domain)
    base_url = f'https://data.commoncrawl.org/crawl-data/{crawl}'
    
    # Download index file
    index_file = f'{crawl}_index.paths.gz'
    if not os.path.exists(index_file):
        download_file(f'{base_url}/cc-index.paths.gz', index_file)
    
    # Find relevant CDX files
    cdx_files = set()
    with gzip.open(index_file, 'rt') as f:
        for line in f:
            if line.startswith('cc-index/collections') and line.endswith('.gz\n'):
                cdx_files.add(f'{base_url}/{line.strip()}')
    
    # Process CDX files
    domain_counts = defaultdict(int)
    cdx_paths = []
    
    for cdx_url in tqdm(cdx_files, desc=f"Processing {domain}"):
        cdx_file = os.path.basename(cdx_url)
        if not os.path.exists(cdx_file):
            download_file(cdx_url, cdx_file)
        
        with gzip.open(cdx_file, 'rt') as f:
            for line in f:
                if line.startswith(f'{surt})'):
                    domain_counts[domain] += 1
                    if cdx_url not in cdx_paths:
                        cdx_paths.append(cdx_url)
    
    available = domain_counts[domain] > 0
    return {
        'domain': domain,
        'available': available,
        'cdx_files': ','.join(cdx_paths),
        'total_urls': domain_counts[domain],
        'crawl_date': crawl,
        'root_page_count': domain_counts.get(f'{surt})/', 0),
        'total_page_count': domain_counts[domain]
    }

def main():
    think_tanks = [
        'brookings.edu',
        'csis.org',
        'carnegieendowment.org',
        'www.heritage.org',
        'www.piie.com',
        'www.wilsoncenter.org',
        'www.americanprogress.org',
        'www.hudson.org',
        'www.rand.org',
        'www.cfr.org',
        'www.atlanticcouncil.org',
        'cato.org',
        'iiss.org',
        'chathamhouse.org',
        'sipri.org',
        'ifri.org',
        'ecfr.eu',
        'lowyinstitute.org',
        'swp-berlin.org',
        'aei.org'
    ]
    
    latest_crawl = get_latest_crawl()
    results = []
    
    print(f"Checking availability in {latest_crawl}...")
    for domain in tqdm(think_tanks):
        try:
            results.append(check_availability(domain, latest_crawl))
        except Exception as e:
            print(f"Error processing {domain}: {e}")
            results.append({
                'domain': domain,
                'available': False,
                'cdx_files': '',
                'total_urls': 0,
                'crawl_date': latest_crawl,
                'root_page_count': 0,
                'total_page_count': 0
            })
    
    df = pd.DataFrame(results)
    print("\nResults:")
    print(df[['domain', 'available', 'total_urls', 'cdx_files']])
    df.to_csv('think_tank_availability.csv', index=False)
    print("\nSaved results to think_tank_availability.csv")

if __name__ == '__main__':
    main()
