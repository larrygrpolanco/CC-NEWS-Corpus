#!/usr/bin/env python3
"""
Script to check the availability of political and international relations sources in Common Crawl.
"""

import os
import sys
import csv
import json
import time
import logging
import argparse
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the parent directory to the path so we can import the utils modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cc_api import check_domain_in_multiple_crawls, DEFAULT_CRAWLS

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

def check_source_availability(source, crawl_ids=None):
    """
    Check the availability of a source in Common Crawl.
    
    Args:
        source (dict): Source information (domain, name, type, etc.)
        crawl_ids (list, optional): List of crawl IDs to check
        
    Returns:
        dict: Results of the availability check
    """
    domain = source['domain']
    logger.info(f"Checking availability of {domain} ({source['name']})")
    
    try:
        # Check the domain in multiple crawls
        results = check_domain_in_multiple_crawls(domain, crawl_ids)
        
        # Add source information to the results
        results['name'] = source['name']
        results['type'] = source['type']
        results['political_leaning'] = source.get('political_leaning', '')
        results['geographic_focus'] = source.get('geographic_focus', '')
        results['primary_topics'] = source.get('primary_topics', '')
        
        # Calculate an overall availability score
        available_crawls = sum(1 for crawl_id, data in results['results'].items() 
                              if data['available'] and not data['error'])
        
        article_availability = False
        for crawl_id, data in results['results'].items():
            if data.get('has_articles', False):
                article_availability = True
                break
        
        results['overall_availability'] = {
            'available_crawls': available_crawls,
            'total_crawls': len(results['results']),
            'availability_score': available_crawls / len(results['results']) if results['results'] else 0,
            'has_articles': article_availability
        }
        
        return results
    
    except Exception as e:
        logger.error(f"Error checking {domain}: {e}")
        return {
            'domain': domain,
            'name': source['name'],
            'type': source['type'],
            'political_leaning': source.get('political_leaning', ''),
            'geographic_focus': source.get('geographic_focus', ''),
            'primary_topics': source.get('primary_topics', ''),
            'error': str(e),
            'results': {},
            'overall_availability': {
                'available_crawls': 0,
                'total_crawls': len(crawl_ids) if crawl_ids else 0,
                'availability_score': 0,
                'has_articles': False
            }
        }

def flatten_results_for_csv(results):
    """
    Flatten the nested results structure for CSV output.
    
    Args:
        results (dict): Results from check_source_availability
        
    Returns:
        dict: Flattened results
    """
    flattened = {
        'domain': results['domain'],
        'name': results['name'],
        'type': results['type'],
        'political_leaning': results['political_leaning'],
        'geographic_focus': results['geographic_focus'],
        'primary_topics': results['primary_topics'],
        'available_crawls': results['overall_availability']['available_crawls'],
        'total_crawls': results['overall_availability']['total_crawls'],
        'availability_score': results['overall_availability']['availability_score'],
        'has_articles': results['overall_availability']['has_articles']
    }
    
    # Add crawl-specific data
    for crawl_id, data in results['results'].items():
        flattened[f'{crawl_id}_available'] = data['available'] and not data['error']
        flattened[f'{crawl_id}_error'] = data.get('error', False)
        flattened[f'{crawl_id}_page_count'] = data.get('page_count', 0)
        flattened[f'{crawl_id}_has_articles'] = data.get('has_articles', False)
        flattened[f'{crawl_id}_article_count'] = data.get('article_count', 0)
    
    return flattened

def main():
    """
    Main function to check source availability.
    """
    parser = argparse.ArgumentParser(description='Check availability of political sources in Common Crawl')
    parser.add_argument('--source-list', type=str, default='../data/source_list.csv',
                        help='Path to the source list CSV file')
    parser.add_argument('--output-dir', type=str, default='../data/availability_results',
                        help='Directory to save results')
    parser.add_argument('--max-workers', type=int, default=5,
                        help='Maximum number of worker threads')
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
    
    # Set crawl IDs
    crawl_ids = args.crawls if args.crawls else DEFAULT_CRAWLS
    
    logger.info(f"Checking source availability in crawls: {', '.join(crawl_ids)}")
    
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
    
    # Check availability of each source
    results = []
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit tasks
        future_to_source = {executor.submit(check_source_availability, source, crawl_ids): source for source in sources}
        
        # Process results as they complete
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                result = future.result()
                results.append(result)
                
                # Log progress
                logger.info(f"Completed {len(results)}/{len(sources)}: {source['domain']}")
                
                # Be polite to the API
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing {source['domain']}: {e}")
    
    # Save detailed results as JSON
    json_output_path = os.path.join(output_dir, f'availability_results_{timestamp}.json')
    with open(json_output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved detailed results to {json_output_path}")
    
    # Flatten results for CSV
    flattened_results = [flatten_results_for_csv(result) for result in results]
    
    # Save flattened results as CSV
    csv_output_path = os.path.join(output_dir, f'availability_results_{timestamp}.csv')
    pd.DataFrame(flattened_results).to_csv(csv_output_path, index=False)
    
    logger.info(f"Saved CSV results to {csv_output_path}")
    
    # Create a summary
    summary = {
        'total_sources': len(sources),
        'sources_checked': len(results),
        'crawls_checked': crawl_ids,
        'timestamp': timestamp,
        'availability_by_crawl': {},
        'availability_by_type': {},
        'top_available_sources': []
    }
    
    # Calculate availability by crawl
    for crawl_id in crawl_ids:
        available_count = sum(1 for result in results if result['results'].get(crawl_id, {}).get('available', False))
        summary['availability_by_crawl'][crawl_id] = {
            'available_count': available_count,
            'percentage': available_count / len(results) * 100 if results else 0
        }
    
    # Calculate availability by source type
    source_types = set(source['type'] for source in sources)
    for source_type in source_types:
        type_results = [result for result in results if result['type'] == source_type]
        available_count = sum(1 for result in type_results if result['overall_availability']['availability_score'] > 0)
        summary['availability_by_type'][source_type] = {
            'total_count': len(type_results),
            'available_count': available_count,
            'percentage': available_count / len(type_results) * 100 if type_results else 0
        }
    
    # Get top available sources
    sorted_results = sorted(results, key=lambda x: x['overall_availability']['availability_score'], reverse=True)
    summary['top_available_sources'] = [
        {
            'domain': result['domain'],
            'name': result['name'],
            'type': result['type'],
            'availability_score': result['overall_availability']['availability_score'],
            'has_articles': result['overall_availability']['has_articles']
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
    print("\nAvailability by crawl:")
    for crawl_id, data in summary['availability_by_crawl'].items():
        print(f"  {crawl_id}: {data['available_count']} sources ({data['percentage']:.1f}%)")
    
    print("\nAvailability by source type:")
    for source_type, data in summary['availability_by_type'].items():
        print(f"  {source_type}: {data['available_count']}/{data['total_count']} sources ({data['percentage']:.1f}%)")
    
    print("\nTop 5 most available sources:")
    for i, source in enumerate(summary['top_available_sources'][:5], 1):
        print(f"  {i}. {source['name']} ({source['domain']}): {source['availability_score']*100:.1f}% available")

if __name__ == "__main__":
    main()
