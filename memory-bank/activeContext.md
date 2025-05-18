# Active Context: Brookings Institution Corpus

## Current Work Focus

- Efficient, local extraction of all Brookings Institution articles from CC-MAIN-2025-18 using index files.
- Validation of the extraction pipeline by building a small pilot corpus (5-10 articles) and cross-checking metadata and text with the live website.
- Preparation for metadata table creation and robust parser development.

## Recent Changes

- Switched from brute-force cdx scanning to targeted extraction using cluster.idx, reducing downloads from 300+ cdx files to just one (cdx-00173.gz).
- Automated the download and filtering of cdx-00173.gz for Brookings articles using a Python-only workflow.
- Saved all Brookings article index matches to brookings_corpus/cdx_work/brookings_cdx_matches.txt (14,692 matches).
- Established a clean, modular directory structure and memory bank for documentation.

## Next Steps

1. **Sample Validation:**
   - Select a small sample (5-10) of Brookings article index lines from brookings_cdx_matches.txt.
   - For each, extract WARC filename, offset, and length.
   - Download the corresponding WARC segment and extract the HTML.
   - Parse brookings.dataLayer and main text from the HTML.
   - Cross-check metadata and text with the live website for accuracy.

2. **Corpus Metadata Table:**
   - Design and implement a standardized metadata table (CSV/DB) with all required fields.
   - Validate parser output against ground truth and document any edge cases.

3. **Pilot Corpus Creation:**
   - Build a small, validated corpus of 5-10 articles with both metadata and cleaned text.
   - Document the extraction and validation process.

4. **Unit Testing:**
   - Develop unit tests for the parser using real HTML samples and expected outputs.

5. **Documentation:**
   - Update README and memory bank with schema, workflow, and validation results.

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
