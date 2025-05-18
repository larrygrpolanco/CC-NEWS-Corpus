import os
import requests
import gzip
from tqdm import tqdm

CC_INDEX_BASE = "https://data.commoncrawl.org/crawl-data"
BROOKINGS_SURT = "edu,brookings)/articles/"

def get_latest_crawl():
    """Get a known-good Common Crawl crawl ID (hardcoded for reliability)."""
    # Use a crawl that is known to have all index files available
    return "CC-MAIN-2024-22"

def download_file(url, local_path):
    """Download a file from a URL with a progress bar. Returns True if successful, False otherwise."""
    if os.path.exists(local_path):
        print(f"File already exists: {local_path}")
        return True
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        print(f"Failed to download {url} (status code: {resp.status_code})")
        return False
    total = int(resp.headers.get('content-length', 0))
    with open(local_path, "wb") as f, tqdm(
        desc=f"Downloading {os.path.basename(local_path)}",
        total=total, unit='B', unit_scale=True
    ) as pbar:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))
    return True

def main():
    os.makedirs("brookings_corpus/raw", exist_ok=True)
    crawl = get_latest_crawl()
    print(f"Using crawl: {crawl}")

    # Download cc-index.paths.gz
    index_paths_url = f"{CC_INDEX_BASE}/{crawl}/cc-index.paths.gz"
    index_paths_local = "brookings_corpus/raw/cc-index.paths.gz"
    download_file(index_paths_url, index_paths_local)

    # Download cluster.idx
    cluster_idx_url = f"{CC_INDEX_BASE}/{crawl}/cc-index/collections/{crawl}/indexes/cluster.idx"
    cluster_idx_local = "brookings_corpus/raw/cluster.idx"
    download_file(cluster_idx_url, cluster_idx_local)

    print("Downloaded cc-index.paths.gz and cluster.idx.")

    # Try to parse cluster.idx to find relevant cdx-*.gz files for Brookings articles
    cluster_idx_local = "brookings_corpus/raw/cluster.idx"
    cdx_files = set()
    try:
        with open(cluster_idx_local, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(BROOKINGS_SURT):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        cdx_file = parts[1]
                        cdx_files.add(cdx_file)
        if cdx_files:
            print(f"Found {len(cdx_files)} relevant cdx-*.gz files for Brookings articles (via cluster.idx).")
    except Exception as e:
        print(f"Could not parse cluster.idx ({e}), will fall back to cc-index.paths.gz.")

    # If no cdx files found, fall back to cc-index.paths.gz
    if not cdx_files:
        print("Falling back to cc-index.paths.gz to get all cdx-*.gz files...")
        index_paths_local = "brookings_corpus/raw/cc-index.paths.gz"
        with gzip.open(index_paths_local, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.endswith(".gz") and "cdx-" in line:
                    cdx_files.add(line)
        print(f"Found {len(cdx_files)} cdx-*.gz files in cc-index.paths.gz.")

    # Save the list for reproducibility
    with open("brookings_corpus/raw/brookings_cdx_files.txt", "w") as out:
        for cdx in sorted(cdx_files):
            out.write(cdx + "\n")
    print("Saved list of relevant cdx-*.gz files to brookings_corpus/raw/brookings_cdx_files.txt")

    # Download and scan cdx-*.gz files for Brookings articles
    cdx_dir = "brookings_corpus/raw/cdx"
    os.makedirs(cdx_dir, exist_ok=True)
    brookings_records = []
    max_articles = 5

    with open("brookings_corpus/raw/brookings_cdx_files.txt") as f:
        cdx_files = [line.strip() for line in f if line.strip()]

    for cdx_file in cdx_files:
        cdx_url = f"{CC_INDEX_BASE}/{crawl}/cc-index/collections/{crawl}/indexes/{cdx_file}"
        cdx_local = os.path.join(cdx_dir, os.path.basename(cdx_file))
        if not download_file(cdx_url, cdx_local):
            continue  # Skip this file if download failed

        try:
            with gzip.open(cdx_local, "rt", encoding="utf-8", errors="replace") as gz:
                for line in gz:
                    if line.startswith(BROOKINGS_SURT):
                        # Example line: SURT TIMESTAMP JSON
                        parts = line.strip().split(" ", 2)
                        if len(parts) == 3:
                            surt, timestamp, raw_json = parts
                            try:
                                import json
                                data = json.loads(raw_json)
                                # Only keep HTML pages
                                if data.get("mime-detected", "").startswith("text/html"):
                                    brookings_records.append({
                                        "surt": surt,
                                        "timestamp": timestamp,
                                        "url": data.get("url"),
                                        "filename": data.get("filename"),
                                        "offset": data.get("offset"),
                                        "length": data.get("length"),
                                        "status": data.get("status"),
                                    })
                                    if len(brookings_records) >= max_articles:
                                        break
                            except Exception as e:
                                print(f"Error parsing JSON: {e}")
                if len(brookings_records) >= max_articles:
                    break
        except Exception as e:
            print(f"Error reading {cdx_local}: {e}")
        if len(brookings_records) >= max_articles:
            break

    print(f"Collected {len(brookings_records)} Brookings article records for testing.")
    # Save metadata for reproducibility
    import csv
    with open("brookings_corpus/raw/brookings_sample_metadata.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["surt", "timestamp", "url", "filename", "offset", "length", "status"])
        writer.writeheader()
        for rec in brookings_records:
            writer.writerow(rec)
    print("Saved sample metadata to brookings_corpus/raw/brookings_sample_metadata.csv")

if __name__ == "__main__":
    main()
