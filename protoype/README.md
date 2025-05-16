# CC-NEWS Corpus Prototypes

This directory contains modular prototypes for processing Common Crawl news data.

## Current Scope
- Testing extraction of political news articles from specific publishers
- Developing parsers for Washington Post, Reuters, AP
- Small-scale testing with sample WARC files
- Building reusable components for larger corpus processing

## Structure
- `process_data/`: WARC processing and article extraction
- `prototypes_mb/`: Documentation of decisions, learnings, and project context

## Usage for AI Agent
1. Access Common Crawl data using `curl http://index.commoncrawl.org/collinfo.json`
2. Download cc-index.paths.gz using `curl https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/cc-index.paths.gz -o cc-index.paths.gz`
3. Decompress cc-index.paths.gz using `gunzip cc-index.paths.gz`
4. Download cluster.idx using `curl https://data.commoncrawl.org/cc-index/collections/CC-MAIN-2025-05/indexes/cluster.idx -o cluster.idx`
5. Filter cluster.idx using `grep` to identify relevant cdx files

## Important Notes
- No Washington Post articles were found in January 2025 crawl data
- `warc_processor.py` in `process_data/` is used for WARC processing
- `washington_post_parser.py` in `process_data/publishers/washington_post/` contains parser implementation

## Next Steps
1. Try processing data from other news sources or timeframes
2. Update `prototypes_mb/` with new findings and decisions
