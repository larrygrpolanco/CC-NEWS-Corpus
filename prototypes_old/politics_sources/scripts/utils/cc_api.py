"""
Common Crawl API utilities for checking source availability and fetching content.
This implementation uses cdx-toolkit for more reliable and polite access to the CDX API.
"""

import json
import time
import random
import logging
import cdx_toolkit

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default crawls to check (most recent first)
DEFAULT_CRAWLS = [
    "CC-MAIN-2025-18",  # April 2025
    "CC-MAIN-2025-13",  # March 2025
    "CC-MAIN-2025-08",  # February 2025
    "CC-MAIN-2025-04",  # January 2025
]


def check_domain_availability(domain, crawl_id):
    """
    Check if a domain is available in a specific crawl using cdx-toolkit.

    Args:
        domain (str): The domain to check (e.g., "example.com")
        crawl_id (str): The ID of the crawl to check (e.g., "CC-MAIN-2025-18")

    Returns:
        dict: Dictionary with availability information
    """
    # Ensure domain doesn't have protocol
    if domain.startswith(("http://", "https://")):
        domain = domain.split("://", 1)[1]

    # Remove trailing slash if present
    if domain.endswith("/"):
        domain = domain[:-1]

    try:
        # Create a CDX fetcher for Common Crawl
        # Note: cdx-toolkit doesn't support custom headers, it uses its own User-Agent
        cdx = cdx_toolkit.CDXFetcher(source="cc")

        # Set the time range to match the specific crawl
        # This is a workaround since cdx-toolkit doesn't support specifying crawls directly
        if crawl_id == "CC-MAIN-2025-18":  # April 2025
            from_ts = "20250401"
            to_ts = "20250430"
        elif crawl_id == "CC-MAIN-2025-13":  # March 2025
            from_ts = "20250301"
            to_ts = "20250331"
        elif crawl_id == "CC-MAIN-2025-08":  # February 2025
            from_ts = "20250201"
            to_ts = "20250228"
        elif crawl_id == "CC-MAIN-2025-04":  # January 2025
            from_ts = "20250101"
            to_ts = "20250131"
        else:
            # Default to the most recent month
            from_ts = "20250401"
            to_ts = "20250430"

        # Check root domain
        root_url = domain
        root_records = []
        root_page_count = 0

        # Try multiple times with increasing delays
        max_retries = 5
        retry_delays = [5, 10, 20, 30, 60]  # seconds

        for retry in range(max_retries):
            try:
                # Get size estimate for root domain
                # Skip size estimate as it's not critical and can cause rate limiting
                # root_size = cdx.get_size_estimate(root_url)
                # logger.info(f"Root domain {root_url} size estimate: {root_size}")

                # Get actual records (limited to 10)
                logger.info(
                    f"Fetching root domain records for {root_url} (attempt {retry+1}/{max_retries})"
                )
                root_records = list(
                    cdx.items(root_url, limit=10, from_ts=from_ts, to=to_ts)
                )
                root_page_count = len(root_records)
                logger.info(f"Found {root_page_count} root domain records")
                break  # Success, exit retry loop

            except Exception as e:
                logger.warning(
                    f"Error getting root domain records (attempt {retry+1}/{max_retries}): {e}"
                )

                if retry < max_retries - 1:  # If not the last retry
                    delay = retry_delays[retry]
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to get root domain records after {max_retries} attempts"
                    )
                    root_page_count = 0
                    root_records = []

        # Add a delay between queries to be polite
        time.sleep(5)

        # Check wildcard domain
        wildcard_url = f"{domain}/*"
        wildcard_records = []
        total_page_count = 0

        # Try multiple times with increasing delays
        for retry in range(max_retries):
            try:
                # Skip size estimate as it's not critical and can cause rate limiting
                # wildcard_size = cdx.get_size_estimate(wildcard_url)
                # logger.info(f"Wildcard domain {wildcard_url} size estimate: {wildcard_size}")

                # Get actual records (limited to 50)
                logger.info(
                    f"Fetching wildcard domain records for {wildcard_url} (attempt {retry+1}/{max_retries})"
                )
                wildcard_records = list(
                    cdx.items(wildcard_url, limit=50, from_ts=from_ts, to=to_ts)
                )
                total_page_count = len(wildcard_records)
                logger.info(f"Found {total_page_count} wildcard domain records")
                break  # Success, exit retry loop

            except Exception as e:
                logger.warning(
                    f"Error getting wildcard domain records (attempt {retry+1}/{max_retries}): {e}"
                )

                if retry < max_retries - 1:  # If not the last retry
                    delay = retry_delays[retry]
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to get wildcard domain records after {max_retries} attempts"
                    )
                    total_page_count = 0
                    wildcard_records = []

        # Determine if domain is available
        available = root_page_count > 0 or total_page_count > 0

        # Get sample URLs
        sample_urls = []
        if wildcard_records:
            for record in wildcard_records[:5]:  # Get up to 5 sample URLs
                url = record.get("url")
                if url:
                    sample_urls.append(url)

        return {
            "domain": domain,
            "crawl_id": crawl_id,
            "available": available,
            "error": False,
            "root_page_count": root_page_count,
            "total_page_count": total_page_count,
            "sample_urls": sample_urls,
        }

    except Exception as e:
        logger.error(f"Error checking domain availability: {e}")
        return {
            "domain": domain,
            "crawl_id": crawl_id,
            "available": False,
            "error": True,
            "root_page_count": 0,
            "total_page_count": 0,
            "sample_urls": [],
            "error_message": str(e),
        }


def get_sample_articles(domain, crawl_id, count=5):
    """
    Get sample article URLs from a domain in a specific crawl.

    Args:
        domain (str): The domain to get samples from
        crawl_id (str): The ID of the crawl to query
        count (int, optional): Number of sample articles to get

    Returns:
        list: List of dictionaries with article information
    """
    # Ensure domain doesn't have protocol
    if domain.startswith(("http://", "https://")):
        domain = domain.split("://", 1)[1]

    # Remove trailing slash if present
    if domain.endswith("/"):
        domain = domain[:-1]

    try:
        # Create a CDX fetcher for Common Crawl
        # Note: cdx-toolkit doesn't support custom headers, it uses its own User-Agent
        cdx = cdx_toolkit.CDXFetcher(source="cc")

        # Set the time range to match the specific crawl
        # This is a workaround since cdx-toolkit doesn't support specifying crawls directly
        if crawl_id == "CC-MAIN-2025-18":  # April 2025
            from_ts = "20250401"
            to_ts = "20250430"
        elif crawl_id == "CC-MAIN-2025-13":  # March 2025
            from_ts = "20250301"
            to_ts = "20250331"
        elif crawl_id == "CC-MAIN-2025-08":  # February 2025
            from_ts = "20250201"
            to_ts = "20250228"
        elif crawl_id == "CC-MAIN-2025-04":  # January 2025
            from_ts = "20250101"
            to_ts = "20250131"
        else:
            # Default to the most recent month
            from_ts = "20250401"
            to_ts = "20250430"

        # Article indicators in URL
        article_indicators = [
            "/article/",
            "/articles/",
            "/story/",
            "/stories/",
            "/news/",
            "/opinion/",
            "/blog/",
            "/blogs/",
            "/analysis/",
            "/commentary/",
            "/report/",
            "/reports/",
            "/publication/",
            "/publications/",
            "/research/",
            "/post/",
            "/posts/",
            "/view/",
            "/read/",
        ]

        # Get records for the domain
        wildcard_url = f"{domain}/*"
        records = []

        # Try multiple times with increasing delays
        max_retries = 5
        retry_delays = [5, 10, 20, 30, 60]  # seconds

        for retry in range(max_retries):
            try:
                # Get actual records (limited to 100)
                logger.info(
                    f"Fetching article records for {wildcard_url} (attempt {retry+1}/{max_retries})"
                )
                records = list(
                    cdx.items(wildcard_url, limit=100, from_ts=from_ts, to=to_ts)
                )
                logger.info(f"Found {len(records)} records")
                break  # Success, exit retry loop

            except Exception as e:
                logger.warning(
                    f"Error getting article records (attempt {retry+1}/{max_retries}): {e}"
                )

                if retry < max_retries - 1:  # If not the last retry
                    delay = retry_delays[retry]
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(
                        f"Failed to get article records after {max_retries} attempts"
                    )
                    records = []

        if not records:
            logger.warning(f"No records found for {domain}")
            return []

        # Filter for likely article URLs
        article_records = []
        for record in records:
            url = record.get("url", "")
            for indicator in article_indicators:
                if indicator in url.lower():
                    article_records.append(record)
                    break

        # If we don't have enough article records, use any records
        if len(article_records) < count:
            article_records = records

        # Get a random sample
        if len(article_records) > count:
            sample_records = random.sample(article_records, count)
        else:
            sample_records = article_records

        # Extract relevant information
        samples = []
        for record in sample_records:
            samples.append(
                {
                    "url": record.get("url"),
                    "timestamp": record.get("timestamp"),
                    "mime": record.get("mime"),
                    "status": record.get("status"),
                    "digest": record.get("digest"),
                    "filename": record.get("filename"),
                    "offset": record.get("offset"),
                    "length": record.get("length"),
                }
            )

        return samples

    except Exception as e:
        logger.error(f"Error getting sample articles: {e}")
        return []


def fetch_warc_record(filename, offset, length):
    """
    Fetch a specific WARC record from Common Crawl.

    Args:
        filename (str): The path to the WARC file
        offset (int): The offset of the record within the WARC file
        length (int): The length of the record

    Returns:
        bytes: The raw content of the WARC record, or None if an error occurred
    """
    # Try multiple times with increasing delays
    max_retries = 5
    retry_delays = [5, 10, 20, 30, 60]  # seconds

    for retry in range(max_retries):
        try:
            # Create a CDX fetcher for Common Crawl
            # Note: cdx-toolkit doesn't support custom headers, it uses its own User-Agent
            cdx = cdx_toolkit.CDXFetcher(source="cc")

            # Use cdx-toolkit to fetch the record
            logger.info(f"Fetching WARC record (attempt {retry+1}/{max_retries})")
            record = cdx.fetch_warc_record(filename, offset, length)

            content = record.content_stream().read()
            logger.info(f"Successfully fetched WARC record ({len(content)} bytes)")
            return content

        except Exception as e:
            logger.warning(
                f"Error fetching WARC record (attempt {retry+1}/{max_retries}): {e}"
            )

            if retry < max_retries - 1:  # If not the last retry
                delay = retry_delays[retry]
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.error(
                    f"Failed to fetch WARC record after {max_retries} attempts"
                )
                return None


if __name__ == "__main__":
    # Example usage
    print("Testing CDX API utilities...")

    # Test domain availability check
    domain = "brookings.edu"
    crawl_id = "CC-MAIN-2025-18"

    print(f"Checking availability of {domain} in {crawl_id}...")
    availability = check_domain_availability(domain, crawl_id)
    print(json.dumps(availability, indent=2))
