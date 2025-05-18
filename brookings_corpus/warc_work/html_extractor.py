import csv
import os
import time
import requests
from warcio.archiveiterator import ArchiveIterator

# ========== USER CONFIGURATION ==========
INPUT_CSV = "brookings_cdx_working_sample_truncated.csv"  # Replace with your chunked CSV filename
HTML_OUT_DIR = "html_raw"
TEMP_WARC = "temp_downloaded.warc.gz"
LOG_CSV = "log_batch.csv"
THROTTLE_SECONDS = 10  # Change this to increase/decrease wait time between downloads
# ========================================

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_warc_segment(filename, offset, length, out_path):
    url = f"https://data.commoncrawl.org/{filename}"
    headers = {"Range": f"bytes={offset}-{offset+length-1}"}
    resp = requests.get(url, headers=headers, stream=True, timeout=120)
    if resp.status_code == 206:
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    elif resp.status_code == 200:
        # Sometimes the server ignores Range and returns the whole file
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    else:
        return False

def extract_html_from_warc(warc_path):
    with open(warc_path, "rb") as stream:
        for record in ArchiveIterator(stream):
            if record.rec_type == "response":
                http_headers = record.http_headers
                content_type = http_headers.get_header("Content-Type") if http_headers else ""
                if content_type and "html" in content_type:
                    raw_html = record.content_stream().read()
                    return raw_html
    return None

def main():
    ensure_dir(HTML_OUT_DIR)
    log_rows = []
    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            digest = row.get("digest") or row.get("content_digest") or row.get("CYR4R4W5TTM4LDGVRROZH2KV3X5XVDIN")
            filename = row["filename"]
            offset = int(row["offset"])
            length = int(row["length"])
            url = row.get("url", "")
            html_out_path = os.path.join(HTML_OUT_DIR, f"{digest}.html")
            if os.path.exists(html_out_path):
                log_rows.append({"digest": digest, "url": url, "status": "skipped (already exists)"})
                continue
            print(f"Processing {digest} ...")
            try:
                ok = download_warc_segment(filename, offset, length, TEMP_WARC)
                if not ok:
                    log_rows.append({"digest": digest, "url": url, "status": f"download failed"})
                    print(f"Download failed for {digest}")
                    continue
                html = extract_html_from_warc(TEMP_WARC)
                if html:
                    with open(html_out_path, "wb") as out_f:
                        out_f.write(html)
                    log_rows.append({"digest": digest, "url": url, "status": "success"})
                    print(f"Extracted HTML for {digest}")
                else:
                    log_rows.append({"digest": digest, "url": url, "status": "no html found"})
                    print(f"No HTML found for {digest}")
            except Exception as e:
                log_rows.append({"digest": digest, "url": url, "status": f"error: {e}"})
                print(f"Error for {digest}: {e}")
            finally:
                if os.path.exists(TEMP_WARC):
                    os.remove(TEMP_WARC)
            time.sleep(THROTTLE_SECONDS)
    # Write log
    with open(LOG_CSV, "w", newline='', encoding='utf-8') as logf:
        writer = csv.DictWriter(logf, fieldnames=["digest", "url", "status"])
        writer.writeheader()
        for row in log_rows:
            writer.writerow(row)
    print(f"Batch complete. Log written to {LOG_CSV}")

if __name__ == "__main__":
    main()
