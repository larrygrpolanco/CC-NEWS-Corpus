# Step 1: Identification – Brookings Institution Corpus

This folder contains everything needed to extract all Brookings Institution articles from the April 2025 Common Crawl (CC-MAIN-2025-18) for research or reproducibility.

---

## **Purpose**

Efficiently identify all Brookings articles from Common Crawl using local index files, minimizing downloads and avoiding rate limits. This step produces a list of all Brookings article records and prepares for the next step: downloading WARC segments and extracting HTML.

---

## **Inputs Required**

- `cluster.idx` – Downloaded from Common Crawl for the target crawl (CC-MAIN-2025-18).
- (Internet access required for downloading cdx-00173.gz if not present.)

---

## **Workflow Steps**

### 1. **Identify Relevant CDX File(s)**
- Use `cluster.idx` to find which cdx-*.gz file(s) contain Brookings articles.
- Example command:
  ```
  grep '^edu,brookings)/articles/' cluster.idx
  ```
- Note the cdx file(s) listed (for April 2025, it's `cdx-00173.gz`).

### 2. **Extract All Brookings Article Index Records**
- Run `find_brookings_in_cdx.py`:
  - Downloads `cdx-00173.gz` if not present.
  - Decompresses and filters for all Brookings articles.
  - Saves all matches to `cdx_work/brookings_cdx_matches.txt`.

### 3. **(Optional) Download/Inspect Other Index Files**
- If you want to repeat for a different crawl, repeat steps above with the new cluster.idx and cdx file(s).

---

## **Scripts in This Folder**

- `find_brookings_in_cdx.py` – Main script for downloading and filtering the relevant cdx file.
- `download_brookings_articles.py` – (Legacy/general) For broader index file management.
- `extract_brookings_html.py` – For the next step: downloading WARC segments and extracting HTML for selected articles.

---

## **Outputs**

- `cdx_work/brookings_cdx_matches.txt` – All Brookings article index records (SURT, timestamp, WARC filename, offset, etc.).
- Ready for WARC/HTML extraction and metadata validation in the next step.

---

## **How to Repeat This Step**

1. Download the latest `cluster.idx` for your target crawl from Common Crawl.
2. Grep for your SURT prefix to find the relevant cdx file(s).
3. Run `find_brookings_in_cdx.py` to extract all Brookings article records.
4. Proceed to WARC/HTML extraction and validation.

---

**This step is complete when you have a local file with all Brookings article index records for your crawl.**
