# Brookings Common Crawl HTML Extraction

This folder contains scripts and instructions for extracting raw HTML files for Brookings articles from Common Crawl WARC files, using a polite, resumable, and chunked workflow.

## Workflow Overview

1. **Split your master CSV** (with WARC info for each article) into manageable chunks (e.g., 100–500 rows).
2. **Place a chunked CSV** in this folder (e.g., `brookings_cdx_working_sample_truncated.csv`).
3. **Run the extraction script** to download each WARC segment, extract the HTML, and save it as a file named by its digest in `html_raw/`.
4. **Logs** are written as CSV for each batch, recording status for every row.
5. **Resume**: The script skips files that already exist, so you can safely re-run or continue after interruption.

## Script: `html_extractor.py`

- **Input:** CSV with columns: `filename`, `offset`, `length`, `digest`, `url`
- **Output:** HTML files in `html_raw/`, named `{digest}.html`
- **Log:** CSV log for each batch (default: `log_batch.csv`)
- **Throttling:** Set `THROTTLE_SECONDS` at the top of the script (default: 10 seconds)
- **Deletes** temporary WARC after extraction to save space

### Usage

1. Place your chunked CSV in this folder.
2. Edit the `INPUT_CSV` variable at the top of `html_extractor.py` if needed.
3. Run:
   ```
   python html_extractor.py
   ```
4. Extracted HTML files will appear in `html_raw/`. Log will be written as `log_batch.csv`.

### Notes

- **All raw HTML is kept in a single folder** for simplicity and reproducibility.
- **No parsing or cleaning** is done at this stage—these are raw HTML files.
- **You can adjust the throttle time** (`THROTTLE_SECONDS`) to avoid rate-limiting.
- **If a file already exists,** it is skipped (safe to resume).
- **Mapping to original URL** is preserved via the log and your CSV.

### Troubleshooting

- If you hit rate limits, increase `THROTTLE_SECONDS`.
- If a download fails, check the log for the error and re-run the script after fixing any issues.

---

This README is designed for both human and AI agent reference, and can be cited in your research methodology for reproducibility.
