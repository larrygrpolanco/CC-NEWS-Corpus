# System Patterns: Brookings Institution Corpus

## System Architecture Overview

- **Data Source:** Common Crawl (CC-MAIN-2025-18), focusing on www.brookings.edu/articles/*
- **Index Filtering:** Use cluster.idx to map SURT prefixes to specific cdx-*.gz files, minimizing downloads.
- **Targeted Extraction:** Download only the relevant cdx-*.gz file(s) (e.g., cdx-00173.gz) and filter for Brookings articles.
- **Metadata & Text Extraction:** For each match, extract WARC filename, offset, and length for precise WARC segment retrieval.
- **Validation:** Cross-check extracted metadata and text with the live website and manual spot-checks.

## Key Technical Decisions

- **SURT Filtering:** Use SURT (Sort-friendly URI Reordering Transform) to efficiently match Brookings articles in index files.
- **Local-First Workflow:** All processing is done locally after initial downloads, avoiding rate limits and repeated API calls.
- **Python-Only Decompression & Filtering:** Use Python's gzip and string matching for cross-platform compatibility and reproducibility.
- **Modular Pipeline:** Each step (index filtering, WARC extraction, metadata parsing, text cleaning) is modular and can be tested/extended independently.
- **Version Control:** All scripts, configuration, and documentation are tracked in git for reproducibility.

## Component Relationships

- **cluster.idx** → identifies relevant **cdx-*.gz** files
- **cdx-*.gz** → contains index records for Brookings articles
- **WARC files** → contain the actual HTML content, accessed via filename/offset/length from cdx records
- **Parser scripts** → extract metadata (brookings.dataLayer) and main text from HTML

## Critical Implementation Paths

1. **Index Filtering:** cluster.idx → cdx-00173.gz
2. **CDX Filtering:** cdx-00173.gz → Brookings article index lines
3. **WARC Extraction:** Use index line metadata to download WARC segments and extract HTML
4. **Metadata/Text Parsing:** Parse brookings.dataLayer and main text from HTML
5. **Validation:** Manual and automated checks against live site and ground truth

## Patterns for Robustness

- **Fail-fast and log errors:** Any extraction or parsing error is logged with context for debugging.
- **Unit testing:** Planned for all parsing and extraction logic, using real HTML samples and ground truth.
- **Schema documentation:** All output tables/files have a documented schema for future use and validation.
