# CC-NEWS Corpus Prototypes

This directory contains modular prototypes for processing Common Crawl news data.

## Current Scope
- Testing extraction of political news articles from specific publishers
- Developing parsers for Washington Post, Reuters, AP
- Small-scale testing with sample WARC files
- Building reusable components for larger corpus processing

## Structure
- Each subfolder contains a complete prototype for one processing stage
- `process_basic_data/`: Initial WARC processing and article extraction
- `parse_basic_data/`: Publisher-specific content parsing
- `prototypes_memory_bank/`: Documentation of decisions and learnings

## Usage
1. Start with `process_basic_data/` to understand WARC file structure
2. Move to specific publisher parsers in `parse_basic_data/`
3. Refer to memory bank for implementation decisions
