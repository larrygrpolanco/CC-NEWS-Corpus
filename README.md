# CC-NEWS-Corpus

## Project Overview
This project involves processing CC-NEWS data using WARC files and developing publisher-specific parsers.

## Directory Structure
The project is organized into the following directory structure:
- data/
  - cc-index/
    - cc-index.paths
    - cluster.idx
  - warc-files/
    - washington_post_article_content.warc
    - washington_post_article.warc.gz
- protoype/
  - process_data/
    - warc_processor.py
    - publishers/
      - washington_post/
        - washington_post_parser.py
  - prototype_mb/
    - projectbrief.md
    - productContext.md
    - activeContext.md

## WARC Processing
The `warc_processor.py` script is used to process WARC files and extract articles from specified domains. It utilizes the `warcio` library to iterate through WARC records and `BeautifulSoup` for HTML parsing.

## Washington Post Parser
A customized parser has been developed for Washington Post articles. The `washington_post_parser.py` script contains functions to extract article text and metadata specific to the Washington Post's HTML structure.

## Usage
To process a WARC file for a specific domain, use the following command:
python protoype/process_data/warc_processor.py data/warc-files/<warc_file_name> <target_domain>

Example:
python protoype/process_data/warc_processor.py data/warc-files/washington_post_article_content.warc washingtonpost.com

## Next Steps
1. Validate the extracted data for accuracy.
2. Consider adding more metadata to the extracted articles.
3. Implement performance benchmarking for the WARC processing pipeline.
