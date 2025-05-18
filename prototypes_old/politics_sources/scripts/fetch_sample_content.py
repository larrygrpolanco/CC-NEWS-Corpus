#!/usr/bin/env python3
"""
Script to fetch sample content from available political and international relations sources.
"""

import os
import sys
import json
import time
import logging
import argparse
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from warcio.archiveiterator import ArchiveIterator
import requests
import io

# Add the parent directory to the path so we can import the utils modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cc_api import get_sample_articles, fetch_warc_record
from utils.html_analyzer import analyze_html_sample

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         'data', 'sample_content', 'fetch_samples.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fetch_and_analyze_sample(domain, name, crawl_id, sample_count=3):
    """
    Fetch and analyze sample articles from a domain.
    
    Args:
        domain (str): The domain to fetch samples from
        name (str): The name of the source
        crawl_id (str): The crawl ID to fetch samples from
        sample_count (int, optional): Number of samples to fetch
        
    Returns:
        dict: Results of the sample fetching and analysis
    """
    logger.info(f"Fetching samples for {domain} ({name}) from {crawl_id}")
    
    try:
        # Get sample article records
        sample_records = get_sample_articles(domain, crawl_id, count=sample_count)
        
        if not sample_records:
            logger.warning(f"No sample articles found for {domain} in {crawl_id}")
            return {
                'domain': domain,
                'name': name,
                'crawl_id': crawl_id,
                'samples_found': 0,
                'samples': []
            }
        
        logger.info(f"Found {len(sample_records)} sample articles for {domain}")
        
        # Fetch and analyze each sample
        samples = []
        for i, record in enumerate(sample_records):
            try:
                # Fetch the WARC record
                warc_content = fetch_warc_record(
                    record['filename'],
                    int(record['offset']),
                    int(record['length'])
                )
                
                if not warc_content:
                    logger.warning(f"Failed to fetch WARC record for {record['url']}")
                    continue
                
                # Parse the WARC record to get the HTML content
                html_content = None
                for warc_record in ArchiveIterator(io.BytesIO(warc_content)):
                    if warc_record.rec_type == 'response':
                        html_content = warc_record.content_stream().read().decode('utf-8', errors='replace')
                        break
                
                if not html_content:
                    logger.warning(f"No HTML content found in WARC record for {record['url']}")
                    continue
                
                # Analyze the HTML content
                analysis_result = analyze_html_sample(html_content, record['url'])
                
                # Save the HTML content to a file
                sample_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'data', 'sample_content', domain.replace('.', '_')
                )
                os.makedirs(sample_dir, exist_ok=True)
                
                sample_filename = f"sample_{i+1}_{crawl_id}.html"
                sample_path = os.path.join(sample_dir, sample_filename)
                
                with open(sample_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # Add to samples
                samples.append({
                    'url': record['url'],
                    'timestamp': record['timestamp'],
                    'filename': record['filename'],
                    'offset': record['offset'],
                    'length': record['length'],
                    'sample_path': sample_path,
                    'content_type': analysis_result['analysis']['content_type'],
                    'extractability': analysis_result['analysis']['extractability']['difficulty'],
                    'metadata': analysis_result['analysis']['metadata'],
                    'content_structure': analysis_result['analysis']['content_structure'],
                    'recommendations': analysis_result['recommendations']
                })
                
                logger.info(f"Successfully analyzed sample {i+1} for {domain}: {record['url']}")
                
                # Be polite to the API
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing sample {i+1} for {domain}: {e}")
        
        return {
            'domain': domain,
            'name': name,
            'crawl_id': crawl_id,
            'samples_found': len(samples),
            'samples': samples
        }
    
    except Exception as e:
        logger.error(f"Error fetching samples for {domain}: {e}")
        return {
            'domain': domain,
            'name': name,
            'crawl_id': crawl_id,
            'error': str(e),
            'samples_found': 0,
            'samples': []
        }

def main():
    """
    Main function to fetch sample content.
    """
    parser = argparse.ArgumentParser(description='Fetch sample content from available political sources')
    parser.add_argument('--results-file', type=str, required=True,
                        help='Path to the availability results JSON file')
    parser.add_argument('--output-dir', type=str, default='../data/sample_content',
                        help='Directory to save sample content')
    parser.add_argument('--max-workers', type=int, default=3,
                        help='Maximum number of worker threads')
    parser.add_argument('--crawl-id', type=str, default='CC-MAIN-2025-18',
                        help='Crawl ID to fetch samples from')
    parser.add_argument('--min-score', type=float, default=0.5,
                        help='Minimum availability score to consider a source')
    parser.add_argument('--sample-count', type=int, default=3,
                        help='Number of samples to fetch per source')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit the number of sources to process (for testing)')
    args = parser.parse_args()
    
    # Resolve paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_path = os.path.abspath(os.path.join(script_dir, args.results_file))
    output_dir = os.path.abspath(os.path.join(script_dir, args.output_dir))
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the availability results
    try:
        with open(results_path, 'r') as f:
            availability_results = json.load(f)
        
        logger.info(f"Read availability results for {len(availability_results)} sources from {results_path}")
    except Exception as e:
        logger.error(f"Error reading availability results: {e}")
        return
    
    # Filter for available sources
    available_sources = []
    for result in availability_results:
        try:
            # Check if the source has a good availability score
            score = result['overall_availability']['availability_score']
            has_articles = result['overall_availability']['has_articles']
            
            if score >= args.min_score and has_articles:
                available_sources.append({
                    'domain': result['domain'],
                    'name': result['name'],
                    'type': result['type'],
                    'availability_score': score
                })
        except KeyError:
            # Skip sources with missing data
            continue
    
    # Sort by availability score
    available_sources.sort(key=lambda x: x['availability_score'], reverse=True)
    
    logger.info(f"Found {len(available_sources)} available sources with score >= {args.min_score}")
    
    # Apply limit if specified
    if args.limit and args.limit < len(available_sources):
        available_sources = available_sources[:args.limit]
        logger.info(f"Limited to {args.limit} sources")
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Fetch and analyze samples
    results = []
    
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        # Submit tasks
        future_to_source = {
            executor.submit(
                fetch_and_analyze_sample, 
                source['domain'], 
                source['name'], 
                args.crawl_id,
                args.sample_count
            ): source for source in available_sources
        }
        
        # Process results as they complete
        for future in as_completed(future_to_source):
            source = future_to_source[future]
            try:
                result = future.result()
                results.append(result)
                
                # Log progress
                logger.info(f"Completed {len(results)}/{len(available_sources)}: {source['domain']}")
                
                # Be polite to the API
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error processing {source['domain']}: {e}")
    
    # Save detailed results as JSON
    json_output_path = os.path.join(output_dir, f'sample_analysis_{timestamp}.json')
    with open(json_output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved detailed results to {json_output_path}")
    
    # Create a summary
    summary = {
        'total_sources': len(available_sources),
        'sources_with_samples': sum(1 for result in results if result['samples_found'] > 0),
        'total_samples': sum(result['samples_found'] for result in results),
        'crawl_id': args.crawl_id,
        'timestamp': timestamp,
        'extractability_by_source': {},
        'content_types': {},
        'metadata_availability': {
            'title': 0,
            'author': 0,
            'date': 0,
            'section': 0
        }
    }
    
    # Calculate extractability by source
    for result in results:
        if result['samples_found'] > 0:
            # Get the average extractability score
            extractability_scores = []
            for sample in result['samples']:
                if 'extractability' in sample:
                    difficulty = sample['extractability']
                    if difficulty == 'easy':
                        extractability_scores.append(3)
                    elif difficulty == 'moderate':
                        extractability_scores.append(2)
                    elif difficulty == 'challenging':
                        extractability_scores.append(1)
                    else:  # difficult
                        extractability_scores.append(0)
            
            if extractability_scores:
                avg_score = sum(extractability_scores) / len(extractability_scores)
                
                if avg_score >= 2.5:
                    difficulty = 'easy'
                elif avg_score >= 1.5:
                    difficulty = 'moderate'
                elif avg_score >= 0.5:
                    difficulty = 'challenging'
                else:
                    difficulty = 'difficult'
                
                summary['extractability_by_source'][result['domain']] = {
                    'name': result['name'],
                    'avg_score': avg_score,
                    'difficulty': difficulty
                }
    
    # Count content types
    for result in results:
        for sample in result['samples']:
            content_type = sample.get('content_type', 'unknown')
            summary['content_types'][content_type] = summary['content_types'].get(content_type, 0) + 1
    
    # Count metadata availability
    total_samples = sum(result['samples_found'] for result in results)
    if total_samples > 0:
        for result in results:
            for sample in result['samples']:
                metadata = sample.get('metadata', {})
                
                if metadata.get('title', {}).get('found', False):
                    summary['metadata_availability']['title'] += 1
                
                if metadata.get('author', {}).get('found', False):
                    summary['metadata_availability']['author'] += 1
                
                if metadata.get('date', {}).get('found', False):
                    summary['metadata_availability']['date'] += 1
                
                if metadata.get('section', {}).get('found', False):
                    summary['metadata_availability']['section'] += 1
        
        # Convert to percentages
        for key in summary['metadata_availability']:
            summary['metadata_availability'][key] = (
                summary['metadata_availability'][key] / total_samples * 100
            )
    
    # Save summary
    summary_output_path = os.path.join(output_dir, f'sample_summary_{timestamp}.json')
    with open(summary_output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Saved summary to {summary_output_path}")
    
    # Print summary to console
    print("\nSample Analysis Summary:")
    print(f"Total sources checked: {len(available_sources)}")
    print(f"Sources with samples: {summary['sources_with_samples']}")
    print(f"Total samples: {summary['total_samples']}")
    
    print("\nContent Types:")
    for content_type, count in summary['content_types'].items():
        print(f"  {content_type}: {count} samples ({count/total_samples*100:.1f}%)")
    
    print("\nMetadata Availability:")
    for metadata_type, percentage in summary['metadata_availability'].items():
        print(f"  {metadata_type}: {percentage:.1f}%")
    
    print("\nTop 5 most extractable sources:")
    sorted_sources = sorted(
        summary['extractability_by_source'].items(),
        key=lambda x: x[1]['avg_score'],
        reverse=True
    )
    for i, (domain, data) in enumerate(sorted_sources[:5], 1):
        print(f"  {i}. {data['name']} ({domain}): {data['difficulty']} ({data['avg_score']:.1f}/3)")

if __name__ == "__main__":
    main()
