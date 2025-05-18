# Politics & International Relations Sources Scripts

This directory contains scripts for checking the availability of political and international relations sources in Common Crawl, fetching sample content, and analyzing the results.

## Setup

1. Install the required dependencies:

```bash
pip install -r ../requirements.txt
```

2. Make sure you have the source list CSV file in the `../data/` directory.

## Scripts

### 1. Check Availability

The `check_availability.py` script checks the availability of sources in Common Crawl using cdx-toolkit.

```bash
# Check availability in the most recent crawl
python check_availability.py

# Check availability in a specific crawl
python check_availability.py --crawls CC-MAIN-2025-18

# Test with a limited number of sources
python check_availability.py --limit 5
```

Options:
- `--source-list`: Path to the source list CSV file (default: `../data/source_list.csv`)
- `--output-dir`: Directory to save results (default: `../data/availability_results`)
- `--crawls`: Specific crawl ID to check (default: the most recent crawl)
- `--limit`: Limit the number of sources to check (for testing)

Output:
- JSON file with detailed results
- CSV file with results in tabular format
- JSON file with summary statistics
- Log file with detailed logging information

The script provides information about page counts:

- **root_page_count**: Number of pages at the root domain (e.g., example.com)
- **total_page_count**: Number of pages under the domain (e.g., example.com/*)

The total_page_count is the most important metric, as it shows how many pages from that domain are actually available in Common Crawl.

### 2. Fetch Sample Content

The `fetch_sample_content.py` script fetches sample content from available sources.

```bash
python fetch_sample_content.py --results-file ../data/availability_results/availability_results_YYYYMMDD_HHMMSS.json --output-dir ../data/sample_content --crawl-id CC-MAIN-2025-18 --min-score 0.5 --sample-count 3
```

Options:
- `--results-file`: Path to the availability results JSON file (required)
- `--output-dir`: Directory to save sample content (default: `../data/sample_content`)
- `--crawl-id`: Crawl ID to fetch samples from (default: `CC-MAIN-2025-18`)
- `--min-score`: Minimum availability score to consider a source (default: 0.5)
- `--sample-count`: Number of samples to fetch per source (default: 3)
- `--limit`: Limit the number of sources to process (for testing)

Output:
- HTML files with sample content
- JSON file with sample analysis results
- JSON file with summary statistics
- Log file with detailed logging information

### 3. Analyze Results

The `analyze_results.py` script analyzes the availability and sample content results and generates a comprehensive report.

```bash
python analyze_results.py --availability-file ../data/availability_results/availability_results_YYYYMMDD_HHMMSS.json --sample-file ../data/sample_content/sample_analysis_YYYYMMDD_HHMMSS.json --output-dir ../reports
```

Options:
- `--availability-file`: Path to the availability results JSON file (required)
- `--sample-file`: Path to the sample analysis JSON file (optional)
- `--output-dir`: Directory to save the report (default: `../reports`)

Output:
- Markdown file with comprehensive report

### 4. Test Availability

The `test_availability.py` script is a simplified version of the check_availability.py script that tests the availability of a few domains.

```bash
python test_availability.py
```

This script is useful for testing the cdx-toolkit implementation with a small number of domains.

## Utility Modules

### cc_api.py

This module provides utilities for interacting with the Common Crawl API using cdx-toolkit, including:
- Checking domain availability in crawls
- Getting sample articles
- Fetching WARC records

### html_analyzer.py

This module provides utilities for analyzing HTML content, including:
- Determining content type (article, homepage, etc.)
- Analyzing metadata (title, author, date, section)
- Analyzing content structure
- Assessing extractability
- Generating extraction recommendations

## Example Workflow

1. Check availability of sources:

```bash
python check_availability.py
```

2. Fetch sample content from available sources:

```bash
python fetch_sample_content.py --results-file ../data/availability_results/availability_results_YYYYMMDD_HHMMSS.json
```

3. Analyze results and generate report:

```bash
python analyze_results.py --availability-file ../data/availability_results/availability_results_YYYYMMDD_HHMMSS.json --sample-file ../data/sample_content/sample_analysis_YYYYMMDD_HHMMSS.json
```

## Implementation Notes

This project uses cdx-toolkit, a specialized library for working with CDX indices from web crawls and archives, including CommonCrawl. It offers several advantages:

1. **Built-in politeness**: The library is designed to be "polite to CDX servers by being single-threaded and serial."
2. **Unified index access**: It "knits together the monthly Common Crawl CDX indices into a single, virtual index."
3. **Proper pagination**: It automatically handles the paged interface for efficient access to large sets of URLs.
4. **Robust error handling**: As a dedicated library, it has better error handling for the specific quirks of the CDX API.

For more information about cdx-toolkit, see the [documentation](https://github.com/cocrawler/cdx_toolkit).
