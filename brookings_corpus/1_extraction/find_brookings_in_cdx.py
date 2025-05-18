import os
import requests
import gzip

CDX_WORK_DIR = "brookings_corpus/cdx_work"
MATCHES_FILE = os.path.join(CDX_WORK_DIR, "brookings_cdx_matches.txt")
BROOKINGS_SURT = "edu,brookings)/articles/"
CDX_TARGET = "cdx-00173.gz"
CDX_URL = f"https://data.commoncrawl.org/cc-index/collections/CC-MAIN-2025-18/indexes/{CDX_TARGET}"

def download_cdx_file():
    """Download the target cdx-*.gz file via HTTPS if not already present."""
    os.makedirs(CDX_WORK_DIR, exist_ok=True)
    local_path = os.path.join(CDX_WORK_DIR, CDX_TARGET)
    if os.path.exists(local_path):
        print(f"{CDX_TARGET} already exists, skipping download.")
        return local_path
    print(f"Downloading {CDX_TARGET} ...")
    with requests.get(CDX_URL, stream=True) as r:
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path

def filter_brookings_in_cdx(local_path):
    """Decompress and filter for Brookings articles, saving to MATCHES_FILE."""
    matches = []
    with gzip.open(local_path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(BROOKINGS_SURT):
                matches.append(line)
    with open(MATCHES_FILE, "w", encoding="utf-8") as out:
        out.writelines(matches)
    print(f"Saved {len(matches)} matches to {MATCHES_FILE}")

def main():
    local_path = download_cdx_file()
    filter_brookings_in_cdx(local_path)

if __name__ == "__main__":
    main()
