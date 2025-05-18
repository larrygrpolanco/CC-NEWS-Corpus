#!/usr/bin/env python3
"""
Script to check the availability of political and international relations sources in Common Crawl.
This implementation uses cdx-toolkit for more reliable and polite access to the CDX API.
"""

import os
import sys
import json
import time
import logging
import argparse
import pandas as pd
from datetime import datetime

# Add the parent directory to the path so we can import the utils modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cc_api import check_domain_availability, DEFAULT_CRAWLS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'data', 'availability_results', 'check_availability.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_source_availability(source, crawl_id):
    """
    Check the availability of a source in Common Crawl.
    
    Args:
        source (dict): Source information (domain, name, type, etc.)
        crawl_id (str): The crawl ID to check
        
    Returns:
        dict: Results of the availability check
    """
    domain = source['domain']
    logger.info(f"Checking availability of {domain} ({source['name']})")
    
    try:
        # Check the domain in the specified crawl
        availability = check_domain_availability(domain, crawl_id)
        
        # Create a simplified result
        result = {
            'domain': domain,
            'name': source['name'],
            'type': source['type'],
            'political_leaning': source.get('political_leaning', ''),
            'geographic_focus': source.get('geographic_focus', ''),
            'primary_topics': source.get('primary_topics', ''),
            'crawl_id': crawl_id,
            'available': availability['available'],
            'error': availability['error'],
            'root_page_count': availability['root_page_count'],
            'total_page_count': availability['total_page_count'],
            'sample_urls': availability['sample_urls'][:3] if len(availability['sample_urls']) > 3 else availability['sample_urls']
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error checking {domain}: {e}")
        return {
            'domain': domain,
            'name': source['name'],
            'type': source['type'],
            'political_leaning': source.get('political_leaning', ''),
            'geographic_focus': source.get('geographic_focus', ''),
            'primary_topics': source.get('primary_topics', ''),
            'crawl_id': crawl_id,
            'available': False,
            'error': True,
            'root_page_count': 0,
            'total_page_count': 0,
            'sample_urls': [],
            'error_message': str(e)
        }

def main():
    """
    Main function to check source availability.
    """
    parser = argparse.ArgumentParser(description='Check availability of political sources in Common Crawl')
    parser.add_argument('--source-list', type=str, default='../data/source_list.csv',
                        help='Path to the source list CSV file')
    parser.add_argument('--output-dir', type=str, default='../data/availability_results',
                        help='Directory to save results')
    parser.add_argument('--crawls', type=str, nargs='+', default=None,
                        help='Specific crawl IDs to check (e.g., CC-MAIN-2025-18)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit the number of sources to check (for testing)')
    args = parser.parse_args()
    
    # Resolve paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_list_path = os.path.abspath(os.path.join(script_dir, args.source_list))
    output_dir = os.path.abspath(os.path.join(script_dir, args.output_dir))
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set crawl ID (use only the most recent crawl by default)
    crawl_id = args.crawls[0] if args.crawls else DEFAULT_CRAWLS[0]
    
    logger.info(f"Checking source availability in crawl: {crawl_id}")
    
    # Read the source list
    try:
        sources_df = pd.read_csv(source_list_path)
        logger.info(f"Read {len(sources_df)} sources from {source_list_path}")
        
        # Apply limit if specified
        if args.limit:
            sources_df = sources_df.head(args.limit)
            logger.info(f"Limited to {args.limit} sources")
        
        # Convert to list of dictionaries
        sources = sources_df.to_dict('records')
    except Exception as e:
        logger.error(f"Error reading source list: {e}")
        return
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Check availability of each source sequentially
    results = []
    
    for i, source in enumerate(sources):
        try:
            # Check availability
            result = check_source_availability(source, crawl_id)
            results.append(result)
            
            # Log progress
            logger.info(f"Completed {i+1}/{len(sources)}: {source['domain']}")
            
        except Exception as e:
            logger.error(f"Error processing {source['domain']}: {e}")
    
    # Save detailed results as JSON
    json_output_path = os.path.join(output_dir, f'availability_results_{timestamp}.json')
    with open(json_output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved detailed results to {json_output_path}")
    
    # Save results as CSV
    csv_output_path = os.path.join(output_dir, f'availability_results_{timestamp}.csv')
    pd.DataFrame(results).to_csv(csv_output_path, index=False)
    
    logger.info(f"Saved CSV results to {csv_output_path}")
    
    # Create a summary
    summary = {
        'total_sources': len(sources),
        'sources_checked': len(results),
        'crawl_id': crawl_id,
        'timestamp': timestamp,
        'availability_by_type': {},
        'top_available_sources': []
    }
    
    # Calculate availability by source type
    source_types = set(source['type'] for source in sources)
    for source_type in source_types:
        type_results = [result for result in results if result['type'] == source_type]
        available_count = sum(1 for result in type_results if result['available'] and not result['error'])
        summary['availability_by_type'][source_type] = {
            'total_count': len(type_results),
            'available_count': available_count,
            'percentage': available_count / len(type_results) * 100 if type_results else 0
        }
    
    # Get top available sources by total page count
    sorted_results = sorted(
        [r for r in results if r['available'] and not r['error']], 
        key=lambda x: x['total_page_count'], 
        reverse=True
    )
    
    summary['top_available_sources'] = [
        {
            'domain': result['domain'],
            'name': result['name'],
            'type': result['type'],
            'root_page_count': result['root_page_count'],
            'total_page_count': result['total_page_count']
        }
        for result in sorted_results[:20]  # Top 20
    ]
    
    # Save summary
    summary_output_path = os.path.join(output_dir, f'availability_summary_{timestamp}.json')
    with open(summary_output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Saved summary to {summary_output_path}")
    
    # Print summary to console
    print("\nAvailability Summary:")
    print(f"Total sources checked: {len(results)}")
    print(f"Crawl ID: {crawl_id}")
    
    print("\nAvailability by source type:")
    for source_type, data in summary['availability_by_type'].items():
        print(f"  {source_type}: {data['available_count']}/{data['total_count']} sources ({data['percentage']:.1f}%)")
    
    print("\nTop 5 sources by page count:")
    for i, source in enumerate(summary['top_available_sources'][:5], 1):
        print(f"  {i}. {source['name']} ({source['domain']}): {source['total_page_count']} pages (root: {source['root_page_count']})")

if __name__ == "__main__":
    main()
