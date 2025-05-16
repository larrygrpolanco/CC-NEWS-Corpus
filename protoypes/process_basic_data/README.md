# WARC Processor Module

## Purpose
This module provides basic functionality for processing WARC files from Common Crawl's CC-NEWS dataset.

## Features
- Filters WARC records by target domain
- Extracts article title and text
- Handles malformed HTML gracefully
- Returns structured article data

## Usage
```python
from warc_processor import process_warc_file

articles = process_warc_file('sample.warc.gz', 'washingtonpost.com')
for article in articles:
    print(f"Title: {article['title']}")
    print(f"URL: {article['url']}")
    print(f"Date: {article['date']}")
    print(f"Text: {article['text'][:200]}...")  # Show first 200 chars
```

## Dependencies
- warcio
- beautifulsoup4
- lxml

## Next Steps
- Add publisher-specific text extraction logic
- Implement batch processing
- Add unit tests
