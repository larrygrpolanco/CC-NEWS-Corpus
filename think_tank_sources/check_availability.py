import requests
import pandas as pd
from tqdm import tqdm
import os
import json

def get_latest_crawl():
    """Get the latest Common Crawl ID"""
    try:
        response = requests.get('http://index.commoncrawl.org/collinfo.json')
        response.raise_for_status()
        return response.json()[0]['id']
    except Exception:
        return 'CC-MAIN-2024-22'

def check_domain(domain):
    """Check if domain exists in Common Crawl"""
    try:
        response = requests.get(
            f'http://index.commoncrawl.org/CC-MAIN-2024-22-index',
            params={'url': f'{domain}/*', 'output': 'json'},
            timeout=30
        )
        response.raise_for_status()
        return len(response.text.strip().split('\n')) > 0
    except Exception:
        return False

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
    
    results = []
    print("Checking domain availability...")
    
    for domain in tqdm(think_tanks):
        exists = check_domain(domain)
        results.append({
            'domain': domain,
            'available': exists
        })
    
    df = pd.DataFrame(results)
    print("\nResults:")
    print(df)
    
    output_file = 'think_tank_availability.csv'
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")

if __name__ == '__main__':
    main()
