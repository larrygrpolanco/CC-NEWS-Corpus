# Progress: Brookings Institution Corpus

## What Works

- **Efficient Index Targeting:** Used cluster.idx to identify the single cdx file (cdx-00173.gz) containing all Brookings articles, avoiding unnecessary downloads.
- **Automated Filtering:** Python script downloads and filters cdx-00173.gz for Brookings articles, saving 14,692 matches to a local file.
- **Cloud-Based Extraction:** Developed and validated a high-speed extraction workflow using AWS EC2 in us-east-1 and S3 access via boto3, enabling rapid, unthrottled retrieval of WARC segments.
- **Scripted Extraction:** `html_extractor_s3.py` reliably extracts raw HTML from WARC segments and logs results for each article.
- **Clean Project Structure:** All scripts, outputs, and documentation are organized in a modular, version-controlled directory structure.
- **Memory Bank Established:** Core documentation files (projectbrief, productContext, systemPatterns, techContext, activeContext) are in place and up to date.

## What's Left to Build

- **Metadata & Text Parsing:** Develop and validate a parser for brookings.dataLayer and main text from HTML.
- **Corpus Metadata Table:** Design and implement a standardized metadata table (CSV/DB) for all extracted articles.
- **Validation Pipeline:** Manual and automated spot-checking of metadata and text against the live website.
- **Unit Tests:** Build comprehensive unit tests for the parser using real HTML samples and ground truth.
- **Pilot Corpus:** Assemble a small, validated pilot corpus (5-10 articles) with both metadata and cleaned text.
- **README & Schema Documentation:** Document the full pipeline, output schema, and validation results.

## Current Status

- Index filtering and match extraction are complete and validated.
- S3-based extraction workflow is ready and documented; project is poised for large-scale HTML extraction on EC2.
- Next major milestone: complete extraction of all Brookings HTML files, then begin metadata/text parsing and validation.

## Known Issues

- **Parser Validation Pending:** Need to ensure all metadata fields are parsed correctly and match the live website.
- **Edge Cases:** Potential for missing or malformed dataLayer fields; must be handled and documented.

## Evolution of Project Decisions

- **Brute-force to Targeted:** Moved from brute-force cdx scanning to cluster.idx-based targeting for massive efficiency gains.
- **Local to Cloud:** Transitioned from local, throttled HTTPS extraction to high-speed, cloud-based S3 extraction on EC2.
- **Python-Only Workflow:** Standardized on Python for all core processing to maximize portability and reproducibility.
- **Documentation-First:** Adopted a rigorous memory bank and documentation strategy to support future work and reproducibility.
