#!/usr/bin/env python3
"""
Test script for the Common Crawl API utilities.
This script tests the basic functionality of the cc_api.py module.
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the utils modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cc_api import (
    query_cdx_api,
    check_domain_availability,
    check_domain_in_multiple_crawls,
    get_sample_articles,
    DEFAULT_CRAWLS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_query_cdx_api(domain, crawl_id):
    """
    Test the query_cdx_api function.
    
    Args:
        domain (str): The domain to query
        crawl_id (str): The crawl ID to query
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Testing query_cdx_api for {domain} in {crawl_id}")
    
    try:
        # Query the CDX API
        records = query_cdx_api(domain, crawl_id)
        
        if records is None:
            logger.error("Failed to query CDX API")
            return False
        
        logger.info(f"Found {len(records)} records")
        
        # Print the first record if available
        if records:
            logger.info(f"First record: {json.dumps(records[0], indent=2)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing query_cdx_api: {e}")
        return False

def test_check_domain_availability(domain, crawl_id):
    """
    Test the check_domain_availability function.
    
    Args:
        domain (str): The domain to check
        crawl_id (str): The crawl ID to check
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Testing check_domain_availability for {domain} in {crawl_id}")
    
    try:
        # Check domain availability
        availability = check_domain_availability(domain, crawl_id)
        
        logger.info(f"Availability: {json.dumps(availability, indent=2)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing check_domain_availability: {e}")
        return False

def test_check_domain_in_multiple_crawls(domain, crawl_ids=None):
    """
    Test the check_domain_in_multiple_crawls function.
    
    Args:
        domain (str): The domain to check
        crawl_ids (list, optional): List of crawl IDs to check
        
    Returns:
        bool: True if successful, False otherwise
    """
    if crawl_ids is None:
        crawl_ids = DEFAULT_CRAWLS[:2]  # Use only the first two crawls for testing
    
    logger.info(f"Testing check_domain_in_multiple_crawls for {domain} in {', '.join(crawl_ids)}")
    
    try:
        # Check domain in multiple crawls
        results = check_domain_in_multiple_crawls(domain, crawl_ids)
        
        logger.info(f"Results: {json.dumps(results, indent=2)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing check_domain_in_multiple_crawls: {e}")
        return False

def test_get_sample_articles(domain, crawl_id, count=2):
    """
    Test the get_sample_articles function.
    
    Args:
        domain (str): The domain to get samples from
        crawl_id (str): The crawl ID to query
        count (int, optional): Number of samples to get
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Testing get_sample_articles for {domain} in {crawl_id}")
    
    try:
        # Get sample articles
        samples = get_sample_articles(domain, crawl_id, count=count)
        
        if not samples:
            logger.warning(f"No sample articles found for {domain} in {crawl_id}")
            return True
        
        logger.info(f"Found {len(samples)} sample articles")
        
        # Print the first sample if available
        if samples:
            logger.info(f"First sample: {json.dumps(samples[0], indent=2)}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing get_sample_articles: {e}")
        return False

def main():
    """
    Main function to run the tests.
    """
    parser = argparse.ArgumentParser(description='Test Common Crawl API utilities')
    parser.add_argument('--domain', type=str, default='brookings.edu',
                        help='Domain to test with (default: brookings.edu)')
    parser.add_argument('--crawl-id', type=str, default='CC-MAIN-2025-18',
                        help='Crawl ID to test with (default: CC-MAIN-2025-18)')
    parser.add_argument('--test', type=str, choices=['all', 'query', 'availability', 'multiple', 'samples'],
                        default='all', help='Which test to run (default: all)')
    args = parser.parse_args()
    
    domain = args.domain
    crawl_id = args.crawl_id
    
    logger.info(f"Testing Common Crawl API utilities with domain {domain} and crawl ID {crawl_id}")
    
    # Run the selected test(s)
    if args.test == 'all' or args.test == 'query':
        success = test_query_cdx_api(domain, crawl_id)
        logger.info(f"query_cdx_api test {'succeeded' if success else 'failed'}")
    
    if args.test == 'all' or args.test == 'availability':
        success = test_check_domain_availability(domain, crawl_id)
        logger.info(f"check_domain_availability test {'succeeded' if success else 'failed'}")
    
    if args.test == 'all' or args.test == 'multiple':
        success = test_check_domain_in_multiple_crawls(domain)
        logger.info(f"check_domain_in_multiple_crawls test {'succeeded' if success else 'failed'}")
    
    if args.test == 'all' or args.test == 'samples':
        success = test_get_sample_articles(domain, crawl_id)
        logger.info(f"get_sample_articles test {'succeeded' if success else 'failed'}")
    
    logger.info("Testing complete")

if __name__ == "__main__":
    main()
