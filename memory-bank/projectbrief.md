# Project Brief: Brookings Institution Corpus

## Objective
Build a high-quality, reproducible research corpus of Brookings Institution articles (www.brookings.edu/articles/*) from the Common Crawl (CC-MAIN-2025-18), focusing on extracting rich metadata (from brookings.dataLayer) and main text for linguistic and persuasion analysis.

## Core Requirements
- Efficiently identify and extract all Brookings articles from the latest Common Crawl using index files (cluster.idx, cdx-*.gz).
- Parse and validate metadata (especially brookings.dataLayer) and main text for each article.
- Create a standardized metadata table (CSV/DB) and organize cleaned text files for analysis.
- Ensure all steps are local, reproducible, and scalable, minimizing unnecessary downloads and API requests.
- Validate extraction accuracy by cross-checking with the live website and manual spot-checks.
- Document the entire pipeline, configuration, and schema for future reproducibility and extension.

## Research Questions
- RQ1: What are the descriptive features of Brookings articles by author(s), topic, and date?
- RQ2: How do linguistic features of persuasion manifest and differ across article types, authors, and over time?

## Scope
- Focus on articles under www.brookings.edu/articles/* from CC-MAIN-2025-18.
- Build a pilot corpus for validation, then scale to the full set.
- Prepare for downstream NLP and persuasion analysis.

## Success Criteria
- A validated, well-documented pilot corpus with accurate metadata and text.
- A robust, version-controlled pipeline for extraction and validation.
- Clear documentation and memory bank for ongoing/future work.
