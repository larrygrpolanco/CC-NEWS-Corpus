# Tech Context: Brookings Institution Corpus

## Technologies Used

- **Python 3**: Main scripting language for all extraction, filtering, and parsing tasks.
- **boto3**: For downloading WARC segments directly from S3 on AWS EC2.
- **awscli**: For configuring AWS credentials and S3 access.
- **requests**: For HTTPS downloads (local/pilot use only).
- **gzip**: For decompressing cdx-*.gz files in Python.
- **warcio**: For reading and extracting records from WARC files.
- **BeautifulSoup4 / lxml**: For HTML parsing, especially to extract brookings.dataLayer.
- **trafilatura**: For robust main content extraction from HTML.
- **pandas**: For metadata table creation and manipulation (planned).
- **tqdm**: For progress bars during downloads and processing.
- **git**: For version control of all scripts, configs, and documentation.

## Development Setup

- **Cloud-first workflow:** Large-scale extraction is performed on AWS EC2 in us-east-1, using S3 and boto3 for high-throughput access.
- **Local-first option:** Small-scale or pilot processing can still be done locally using HTTPS and requests.
- **Directory structure**:
  - `brookings_corpus/`: All scripts and outputs for the Brookings pipeline.
  - `brookings_corpus/cdx_work/`: All cdx-*.gz files and filtered matches.
  - `memory-bank/`: Project documentation and context files.
  - `CC_docs/`: Research plan, methodology, and reference documentation.
- **Virtual environment**: Python venv recommended for dependency isolation.

## Technical Constraints

- **File size**: cdx-*.gz and WARC files can be very large (hundreds of MB to GB). Scripts must stream/process line-by-line to avoid memory issues.
- **Cross-platform**: All code should work on macOS, Linux, and AWS EC2, avoiding shell-specific commands.
- **Reproducibility**: All steps, parameters, and outputs must be documented and version-controlled.
- **Network**: Cloud workflow eliminates public rate limits and enables rapid extraction; local workflow requires a stable, fast connection for initial downloads.

## Dependencies

- Python packages: boto3, awscli, requests, gzip (stdlib), warcio, beautifulsoup4, lxml, trafilatura, pandas, tqdm
- No reliance on wget or shell utilities for core pipeline (for portability).

## Tool Usage Patterns

- **Index filtering**: Use cluster.idx and cdx-*.gz with Python, not shell tools.
- **WARC extraction**: Use warcio and boto3 for byte-range downloads from S3 (cloud), or requests (local).
- **HTML parsing**: Use BeautifulSoup4/lxml for metadata, trafilatura for main text.
- **Validation**: Use pandas and manual spot-checks for metadata and text validation.
