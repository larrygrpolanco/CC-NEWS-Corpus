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
│   ├── test_cc_api.py           # Test script for Common Crawl API utilities
│   ├── test_html_analyzer.py    # Test script for HTML analyzer utilities
│   ├── README.md                # Documentation for scripts
│   └── utils/
│       ├── cc_api.py            # Common Crawl API utilities
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

1. Test the setup with the test scripts:
   ```
   python scripts/test_cc_api.py
   python scripts/test_html_analyzer.py
   ```

2. Run the main scripts in sequence:
   ```
   python scripts/check_availability.py
   python scripts/fetch_sample_content.py --results-file data/availability_results/availability_results_YYYYMMDD_HHMMSS.json
   python scripts/analyze_results.py --availability-file data/availability_results/availability_results_YYYYMMDD_HHMMSS.json --sample-file data/sample_content/sample_analysis_YYYYMMDD_HHMMSS.json
   ```
