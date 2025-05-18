# Active Context: Brookings Institution Corpus

## Current Work Focus

- Slow, chunked, and polite extraction of all Brookings Institution articles as raw HTML from Common Crawl WARC files, using a robust, resumable, and well-documented workflow.
- All planning, validation, and script setup is complete; the project is now in the data collection phase.

## Recent Changes

- Decided against AWS Athena/cloud extraction due to already having all WARC locations from the CDX.
- Developed and documented a script (`html_extractor.py`) for polite, chunked extraction of HTML, with user-configurable throttling and robust logging.
- Established a single-folder organization for all raw HTML (`html_raw/`), with each file named by its digest for easy mapping to the master CSV.
- Created a concise README for future reference and reproducibility.

## Next Steps

- Manually run the extraction script on each chunked CSV, monitoring logs and adjusting throttle as needed to avoid rate-limiting.
- Continue until all HTML files are collected.
- The next major update will be after HTML extraction is complete, or if issues arise during extraction.

## Active Decisions & Considerations

- **Index targeting:** Always use cluster.idx to minimize unnecessary downloads.
- **Python-only processing:** Avoid shell tools for maximum portability and reproducibility.
- **Validation-first:** Prioritize manual and automated validation before scaling up.
- **Documentation:** Maintain up-to-date memory bank and code comments for future work.

## Important Patterns & Learnings

- Using cluster.idx for index targeting is critical for efficiency.
- Local, modular, and version-controlled workflows are essential for reproducibility.
- Manual spot-checking and unit tests are necessary to ensure extraction accuracy.
- All code, configuration, and documentation should be kept in sync and under version control.
