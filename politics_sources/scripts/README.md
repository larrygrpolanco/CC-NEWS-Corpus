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

The `check_availability.py` script checks the availability of sources in Common Crawl.

```bash
python check_availability.py --source-list ../data/source_list.csv --output-dir ../data/availability_results --max-workers 5 --crawls CC-MAIN-2025-18 CC-MAIN-2025-13 CC-MAIN-2025-08 CC-MAIN-2025-04
```

Options:
- `--source-list`: Path to the source list CSV file (default: `../data/source_list.csv`)
- `--output-dir`: Directory to save results (default: `../data/availability_results`)
- `--max-workers`: Maximum number of worker threads (default: 5)
- `--crawls`: Specific crawl IDs to check (default: the 4 most recent crawls)
- `--limit`: Limit the number of sources to check (for testing)

Output:
- JSON file with detailed results
- CSV file with flattened results
- JSON file with summary statistics
- Log file with detailed logging information

### 2. Fetch Sample Content

The `fetch_sample_content.py` script fetches sample content from available sources.

```bash
python fetch_sample_content.py --results-file ../data/availability_results/availability_results_YYYYMMDD_HHMMSS.json --output-dir ../data/sample_content --max-workers 3 --crawl-id CC-MAIN-2025-18 --min-score 0.5 --sample-count 3
```

Options:
- `--results-file`: Path to the availability results JSON file (required)
- `--output-dir`: Directory to save sample content (default: `../data/sample_content`)
- `--max-workers`: Maximum number of worker threads (default: 3)
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

## Utility Modules

### cc_api.py

This module provides utilities for interacting with the Common Crawl API, including:
- Querying the CDX API for domains
- Checking domain availability in crawls
- Fetching WARC records
- Getting sample articles

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

## Testing

To test the scripts with a limited number of sources, use the `--limit` option:

```bash
python check_availability.py --limit 5
python fetch_sample_content.py --results-file ../data/availability_results/availability_results_YYYYMMDD_HHMMSS.json --limit 3
```

This will process only a small number of sources, which is useful for testing the scripts before running them on the full dataset.
