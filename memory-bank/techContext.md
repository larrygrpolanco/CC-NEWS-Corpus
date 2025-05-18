# Tech Context: Brookings Institution Corpus

## Technologies Used

- **Python 3**: Main scripting language for all extraction, filtering, and parsing tasks.
- **requests**: For downloading index and WARC files via HTTPS.
- **gzip**: For decompressing cdx-*.gz files in Python.
- **warcio**: For reading and extracting records from WARC files.
- **BeautifulSoup4 / lxml**: For HTML parsing, especially to extract brookings.dataLayer.
- **trafilatura**: For robust main content extraction from HTML.
- **pandas**: For metadata table creation and manipulation (planned).
- **tqdm**: For progress bars during downloads and processing.
- **git**: For version control of all scripts, configs, and documentation.

## Development Setup

- **Local-first workflow**: All processing is done on the user's local machine after initial downloads.
- **Directory structure**:
  - `brookings_corpus/`: All scripts and outputs for the Brookings pipeline.
  - `brookings_corpus/cdx_work/`: All cdx-*.gz files and filtered matches.
  - `memory-bank/`: Project documentation and context files.
  - `CC_docs/`: Research plan, methodology, and reference documentation.
- **Virtual environment**: Python venv recommended for dependency isolation.

## Technical Constraints

- **File size**: cdx-*.gz and WARC files can be very large (hundreds of MB to GB). Scripts must stream/process line-by-line to avoid memory issues.
- **Cross-platform**: All code should work on macOS and Linux, avoiding shell-specific commands.
- **Reproducibility**: All steps, parameters, and outputs must be documented and version-controlled.
- **Network**: Initial downloads require a stable, fast connection; all further processing is local.

## Dependencies

- Python packages: requests, gzip (stdlib), warcio, beautifulsoup4, lxml, trafilatura, pandas, tqdm
- No reliance on AWS CLI, wget, or shell utilities for core pipeline (for portability).

## Tool Usage Patterns

- **Index filtering**: Use cluster.idx and cdx-*.gz with Python, not shell tools.
- **WARC extraction**: Use warcio and requests for byte-range downloads.
- **HTML parsing**: Use BeautifulSoup4/lxml for metadata, trafilatura for main text.
- **Validation**: Use pandas and manual spot-checks for metadata and text validation.
