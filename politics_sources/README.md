# Politics & International Relations Sources in Common Crawl

This project aims to identify and analyze the availability of political and international relations content in the Common Crawl dataset, with a focus on recent crawls.

## Project Structure

```
politics_sources/
├── data/
│   ├── source_list.csv          # Master list of all sources to check
│   ├── availability_results/    # Results from availability checks
│   └── sample_content/          # Sample content from available sources
├── scripts/
│   ├── check_availability.py    # Main script to check source availability
│   ├── analyze_results.py       # Analyze and summarize results
│   ├── fetch_sample_content.py  # Fetch sample content from available sources
│   ├── test_availability.py     # Test script for availability checking
│   ├── README.md                # Documentation for scripts
│   └── utils/
│       ├── cc_api.py            # Common Crawl API utilities using cdx-toolkit
│       └── html_analyzer.py     # Analyze HTML structure of samples
├── reports/
│   ├── availability_report.md   # Final report on source availability (generated)
│   ├── report_template.md       # Template for availability report
│   └── research_considerations.md # Research considerations for persuasive language analysis
└── requirements.txt             # Python dependencies
```

## Purpose

This project is designed to:

1. Check the availability of various political and international relations sources in Common Crawl
2. Focus on recent crawls, particularly CC-MAIN-2025-18 (April 2025)
3. Analyze the structure and content of available sources
4. Generate a comprehensive report on availability and suitability for corpus creation

## Source Categories

We're examining sources across several categories:

1. Think Tanks & Policy Institutes
2. International Policy Journals & Magazines
3. International Organizations & NGOs
4. Political Commentary Sites
5. Academic & Research Platforms
6. Regional Politics & International Relations
7. Independent Political Analysis

## Research Focus

The ultimate goal is to identify suitable sources for creating a corpus to study persuasive language in political and international relations content, with a focus on:

- Linguistic features of persuasion
- Variations across different types of sources
- Changes in persuasive language around significant events

See [research_considerations.md](reports/research_considerations.md) for a detailed discussion of research considerations, theoretical frameworks, and potential research questions for analyzing persuasive language in political and international relations content.

## Usage

### Prerequisites

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure you have the source list CSV file in the `data/` directory.

### Checking Source Availability

```bash
# Check availability in the most recent crawl (default)
python scripts/check_availability.py

# Check availability in a specific crawl
python scripts/check_availability.py --crawls CC-MAIN-2025-18

# Test with a limited number of sources
python scripts/check_availability.py --limit 5
```

The script will generate:
- A JSON file with detailed results
- A CSV file with the same results in a tabular format
- A JSON file with summary statistics
- A log file with detailed logging information

### Understanding the Results

The availability check provides the following information for each source:

- **available**: Whether the domain is available in the crawl
- **root_page_count**: Number of pages at the root domain (e.g., example.com)
- **total_page_count**: Number of pages under the domain (e.g., example.com/*)
- **sample_urls**: Sample URLs from the domain that were found in the crawl

The total_page_count is the most important metric, as it shows how many pages from that domain are actually available in Common Crawl. A higher count means more content is available for your corpus.

## Implementation Notes

This project uses cdx-toolkit, a specialized library for working with CDX indices from web crawls and archives, including CommonCrawl. It offers several advantages:

1. **Built-in politeness**: The library is designed to be "polite to CDX servers by being single-threaded and serial."
2. **Unified index access**: It "knits together the monthly Common Crawl CDX indices into a single, virtual index."
3. **Proper pagination**: It automatically handles the paged interface for efficient access to large sets of URLs.
4. **Robust error handling**: As a dedicated library, it has better error handling for the specific quirks of the CDX API.

For more information about cdx-toolkit, see the [documentation](https://github.com/cocrawler/cdx_toolkit).
