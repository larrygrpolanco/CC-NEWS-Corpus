#!/usr/bin/env python3
"""
Test script to check the availability of a few political and international relations sources in Common Crawl.
This script uses cdx-toolkit for more reliable and polite access to the CDX API.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the utils modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cc_api import check_domain_availability, DEFAULT_CRAWLS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test domains
TEST_DOMAINS = [
    "brookings.edu",
    "csis.org",
    "carnegieendowment.org"
]

def main():
    """
    Main function to test availability checking with cdx-toolkit.
    """
    # Use the most recent crawl
    crawl_id = DEFAULT_CRAWLS[0]
    
    print(f"Testing availability checking with cdx-toolkit in {crawl_id}")
    print("This will show both root_page_count and total_page_count")
    print("-" * 80)
    
    results = []
    
    for domain in TEST_DOMAINS:
        print(f"\nChecking {domain}...")
        
        # Check availability
        availability = check_domain_availability(domain, crawl_id)
        
        # Print results
        print(f"  Available: {availability['available']}")
        print(f"  Root page count: {availability['root_page_count']}")
        print(f"  Total page count: {availability['total_page_count']}")
        
        if availability['sample_urls']:
            print(f"  Sample URLs:")
            for url in availability['sample_urls'][:3]:
                print(f"    - {url}")
        
        # Add to results
        results.append({
            'domain': domain,
            'available': availability['available'],
            'root_page_count': availability['root_page_count'],
            'total_page_count': availability['total_page_count'],
            'sample_urls': availability['sample_urls'][:3] if availability['sample_urls'] else []
        })
    
    # Save results
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'test_results')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(output_dir, f'test_results_{timestamp}.json')
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_path}")
    
    # Print summary
    print("\nSummary:")
    print(f"Total domains tested: {len(TEST_DOMAINS)}")
    print(f"Available domains: {sum(1 for r in results if r['available'])}")
    
    # Calculate total pages
    total_root_pages = sum(r['root_page_count'] for r in results)
    total_all_pages = sum(r['total_page_count'] for r in results)
    
    print(f"Total root pages: {total_root_pages}")
    print(f"Total pages (including subpages): {total_all_pages}")
    print(f"Ratio of total pages to root pages: {total_all_pages / total_root_pages if total_root_pages > 0 else 'N/A'}")

if __name__ == "__main__":
    main()
