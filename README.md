# CC-NEWS-Corpus

A reproducible pipeline for building a research corpus of Brookings Institution articles extracted from the [Common Crawl](https://commoncrawl.org/) web archive.

---

## Overview

This project extracts all publicly archived articles from the Brookings Institution (`www.brookings.edu/articles/*`) from Common Crawl's CC-MAIN-2025-18 snapshot. The result is a structured corpus of over 13,000 policy articles with rich metadata — suitable for NLP research, computational social science, and discourse analysis.

The pipeline is fully local and reproducible, with an optional cloud-accelerated path using AWS EC2 + S3 for large-scale extraction.

---

## Pipeline

The workflow runs in three phases:

### Phase 1 — Identification
Use Common Crawl's CDX index to find all Brookings articles without downloading the full archive. The script targets the relevant CDX file using `cluster.idx` and filters with SURT (Sort-friendly URI Reordering Transform) to find all matching URLs.

**Output:** 14,692 article records with WARC file locations, byte offsets, and content digests.

### Phase 2 — Extraction
Download only the relevant WARC segments (not the full archive) and extract raw HTML files. Two extraction modes:
- **Local (HTTPS)** — for small batches, throttled to avoid rate limits
- **Cloud (AWS S3 + EC2)** — for full-corpus extraction, faster with no rate limiting

**Output:** Raw HTML files saved to `html_raw/`, named by content digest.

### Phase 3 — Analysis
Parse extracted HTML to retrieve article text and Brookings-specific `dataLayer` metadata (author, topic, region, program, publication date, content type). Analyze the corpus for descriptive statistics and linguistic features.

---

## Corpus Statistics

| Metric | Value |
|---|---|
| Articles identified in Common Crawl | 14,692 |
| Articles successfully extracted | 13,327 |
| Total words | 16,285,024 |
| Average words per article | ~1,222 |
| Publication range | 2010–2024 |

**Content breakdown:**
- 75.7% Commentary, 24.3% Research
- Article types: Op-ed (16.2%), Podcast (4.2%), Testimony (1.8%)
- Top topics: U.S. Government & Politics (12.4%), U.S. Economy (9.7%), Education (5.7%)
- Top programs: Foreign Policy (27.8%), Economic Studies (19.4%), Governance Studies (16.3%)
- Regional coverage: 40.6% of articles include a regional focus

---

## Project Structure

```
CC-NEWS-Corpus/
├── brookings_corpus/
│   ├── 1_identification/          # Phase 1: CDX index search
│   │   ├── find_brookings_in_cdx.py
│   │   ├── download_brookings_articles.py
│   │   ├── cdx_work/              # CDX index files and filtered matches
│   │   └── cluster.idx            # Common Crawl cluster index
│   └── 2_extraction/              # Phase 2: WARC extraction
│       ├── html_extractor.py      # Local/HTTPS extraction
│       ├── html_extractor_s3.py   # Cloud extraction via AWS S3
│       └── EC2_guide.md           # Setup guide for EC2
├── html_raw/                      # 13,327 extracted HTML files
├── Corpus_docs/                   # Research documentation and references
├── memory-bank/                   # Project context and architecture notes
├── requirements.txt
└── LICENSE
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- AWS credentials configured (for cloud extraction only)

### Install

```bash
git clone https://github.com/larrygrpolanco/CC-NEWS-Corpus.git
cd CC-NEWS-Corpus
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the Pipeline

**Phase 1 — Find articles in Common Crawl:**
```bash
python brookings_corpus/1_identification/find_brookings_in_cdx.py
# Output: brookings_corpus/1_identification/cdx_work/brookings_cdx_matches.txt
```

**Phase 2a — Extract HTML locally (small batches):**
```bash
# Edit html_extractor.py to set INPUT_CSV, OUTPUT_DIR, and throttle settings
python brookings_corpus/2_extraction/html_extractor.py
# Output: HTML files in html_raw/
```

**Phase 2b — Extract HTML via AWS (full corpus):**
```bash
# See brookings_corpus/2_extraction/EC2_guide.md for EC2 setup
python brookings_corpus/2_extraction/html_extractor_s3.py
# Output: HTML files in html_raw/
```

---

## Output

| File/Directory | Description |
|---|---|
| `html_raw/*.html` | Raw HTML files, named by content digest |
| `cdx_work/brookings_cdx_matches.csv` | Metadata for all identified articles (URL, WARC offset, digest, timestamp) |
| `log_batch.csv` | Extraction log with status for each processed file |

---

## Research Context

This corpus was built to support two research questions:

1. **Descriptive analysis** — What are the characteristics of Brookings articles by author, topic, program, and date?
2. **Linguistic analysis** — How do features of persuasion manifest and differ across article types, authors, and over time?

The Brookings Institution is a major U.S. policy think tank, making its publication archive a valuable source for studying expert policy communication and public discourse.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
