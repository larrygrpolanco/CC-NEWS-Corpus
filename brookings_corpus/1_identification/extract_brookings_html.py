import os
import csv
import requests
from warcio.archiveiterator import ArchiveIterator

CC_INDEX_BASE = "https://data.commoncrawl.org/"

def download_warc_segment(warc_path, offset, length, local_path):
    """Download a byte range from a WARC file."""
    url = CC_INDEX_BASE + warc_path
    headers = {"Range": f"bytes={offset}-{int(offset)+int(length)-1}"}
    resp = requests.get(url, headers=headers, stream=True)
    if resp.status_code not in (200, 206):
        raise Exception(f"Failed to download WARC segment: {resp.status_code}")
    with open(local_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

def extract_html_from_warc(warc_file, output_html):
    """Extract HTML content from a WARC file segment."""
    with open(warc_file, "rb") as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == "response":
                payload = record.content_stream().read()
                # Try to decode as utf-8, fallback to latin1
                try:
                    html = payload.decode("utf-8")
                except Exception:
                    html = payload.decode("latin1", errors="replace")
                with open(output_html, "w", encoding="utf-8") as out:
                    out.write(html)
                return True
    return False

def main():
    os.makedirs("brookings_corpus/sample_html", exist_ok=True)
    with open("brookings_corpus/raw/brookings_sample_metadata.csv", newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            warc_path = row["filename"]
            offset = row["offset"]
            length = row["length"]
            url = row["url"]
            local_warc = f"brookings_corpus/sample_html/sample_{i+1}.warc.gz"
            output_html = f"brookings_corpus/sample_html/sample_{i+1}.html"
            print(f"Downloading WARC segment for: {url}")
            download_warc_segment(warc_path, offset, length, local_warc)
            print(f"Extracting HTML to: {output_html}")
            success = extract_html_from_warc(local_warc, output_html)
            if not success:
                print(f"Failed to extract HTML for {url}")

if __name__ == "__main__":
    main()
