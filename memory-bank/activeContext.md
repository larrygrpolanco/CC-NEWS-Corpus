# Active Context: Brookings Institution Corpus

## Current Work Focus

- High-speed extraction of all Brookings Institution articles as raw HTML from Common Crawl WARC files, using a robust, resumable, and well-documented workflow.
- Extraction is now performed on AWS EC2 in us-east-1, accessing WARC data directly from S3 for maximum speed and reliability.
- The project is in the large-scale data collection phase, leveraging the new cloud-based workflow.

## Recent Changes

- Migrated extraction workflow from local, throttled HTTPS downloads to cloud-based, unthrottled S3 access on EC2.
- Developed and documented a new script (`html_extractor_s3.py`) for S3-based extraction using boto3.
- Created a beginner-friendly EC2 setup guide (`EC2_guide.md`) to support reproducibility and ease of use.
- Updated documentation and memory bank to reflect the new workflow and technical decisions.

## Next Steps

- Run the S3-based extraction script on EC2 to collect all HTML files for Brookings articles.
- Download the resulting HTML files to local storage for further processing.
- Begin development and validation of the metadata and text parser for brookings.dataLayer and main content.
- Assemble and validate a pilot corpus, then scale up to the full dataset.
- Continue updating documentation and memory bank as the project progresses.

## Active Decisions & Considerations

- **Cloud-first extraction:** Use EC2 in us-east-1 and S3 for all large-scale WARC extraction tasks.
- **Python-only processing:** Maintain portability and reproducibility by using Python for all core steps.
- **Validation-first:** Prioritize manual and automated validation before scaling up.
- **Documentation:** Keep memory bank and code comments up to date for future work.

## Important Patterns & Learnings

- Cloud-based extraction (EC2 + S3) is dramatically faster and more reliable for large-scale Common Crawl work.
- Modular, version-controlled workflows and clear documentation are essential for reproducibility.
- Manual spot-checking and unit tests remain critical for ensuring extraction and parsing accuracy.
