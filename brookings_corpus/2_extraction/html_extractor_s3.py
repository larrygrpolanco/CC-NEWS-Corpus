import csv
import os
import sys

# Dependency check
try:
    import boto3
except ImportError:
    print("ERROR: The 'boto3' package is not installed. Please run: pip3 install boto3")
    sys.exit(1)
try:
    from warcio.archiveiterator import ArchiveIterator
except ImportError:
    print(
        "ERROR: The 'warcio' package is not installed. Please run: pip3 install warcio"
    )
    sys.exit(1)

# ========== USER CONFIGURATION ==========
INPUT_CSV = "brookings_cdx_working_sample.csv"  # Your input CSV
HTML_OUT_DIR = "html_raw"
TEMP_WARC = "temp_downloaded.warc.gz"
LOG_CSV = "log_batch.csv"
COMMONCRAWL_BUCKET = "commoncrawl"
# ========================================


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def check_aws_credentials():
    import boto3

    session = boto3.Session()
    credentials = session.get_credentials()
    if not credentials or not credentials.access_key:
        print(
            "ERROR: AWS credentials not found. Please run 'aws configure' and ensure you have access to S3."
        )
        sys.exit(1)


def download_warc_segment_s3(s3_client, filename, offset, length, out_path):
    # Download a byte range from S3 and save to out_path
    s3_key = filename
    byte_range = f"bytes={offset}-{offset+length-1}"
    try:
        resp = s3_client.get_object(
            Bucket=COMMONCRAWL_BUCKET, Key=s3_key, Range=byte_range
        )
        with open(out_path, "wb") as f:
            for chunk in resp["Body"].iter_chunks(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading {s3_key} [{byte_range}]: {e}")
        return False


def extract_html_from_warc(warc_path):
    try:
        with open(warc_path, "rb") as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type == "response":
                    http_headers = record.http_headers
                    content_type = (
                        http_headers.get_header("Content-Type") if http_headers else ""
                    )
                    if content_type and "html" in content_type:
                        raw_html = record.content_stream().read()
                        return raw_html
    except Exception as e:
        print(f"Error reading/parsing WARC file: {e}")
    return None


def main():
    print("Brookings Common Crawl HTML Extraction")
    print("=====================================")
    print(
        "This script will download and extract HTML files from Common Crawl using your CSV input."
    )
    print("Output directory will be:", os.path.abspath(HTML_OUT_DIR))
    input("Press Enter to continue...")

    ensure_dir(HTML_OUT_DIR)
    check_aws_credentials()
    log_rows = []
    processed = 0
    skipped = 0
    failed = 0
    success = 0

    import boto3

    s3_client = boto3.client("s3")
    try:
        with open(INPUT_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                digest = (
                    row.get("digest")
                    or row.get("content_digest")
                    or row.get("CYR4R4W5TTM4LDGVRROZH2KV3X5XVDIN")
                )
                filename = row["filename"]
                offset = int(row["offset"])
                length = int(row["length"])
                url = row.get("url", "")
                html_out_path = os.path.join(HTML_OUT_DIR, f"{digest}.html")
                processed += 1
                if os.path.exists(html_out_path):
                    log_rows.append(
                        {
                            "digest": digest,
                            "url": url,
                            "status": "skipped (already exists)",
                        }
                    )
                    skipped += 1
                    print(f"[{processed}] Skipped {digest} (already exists)")
                    continue
                print(f"[{processed}] Processing {digest} ...")
                try:
                    ok = download_warc_segment_s3(
                        s3_client, filename, offset, length, TEMP_WARC
                    )
                    if not ok:
                        log_rows.append(
                            {"digest": digest, "url": url, "status": f"download failed"}
                        )
                        failed += 1
                        print(f"  Download failed for {digest}")
                        continue
                    html = extract_html_from_warc(TEMP_WARC)
                    if html:
                        with open(html_out_path, "wb") as out_f:
                            out_f.write(html)
                        log_rows.append(
                            {"digest": digest, "url": url, "status": "success"}
                        )
                        success += 1
                        print(f"  Extracted HTML for {digest}")
                    else:
                        log_rows.append(
                            {"digest": digest, "url": url, "status": "no html found"}
                        )
                        failed += 1
                        print(f"  No HTML found for {digest}")
                except Exception as e:
                    log_rows.append(
                        {"digest": digest, "url": url, "status": f"error: {e}"}
                    )
                    failed += 1
                    print(f"  Error for {digest}: {e}")
                finally:
                    if os.path.exists(TEMP_WARC):
                        os.remove(TEMP_WARC)
    except FileNotFoundError:
        print(
            f"ERROR: Input CSV file '{INPUT_CSV}' not found. Please upload it to the instance."
        )
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Write log
    with open(LOG_CSV, "w", newline="", encoding="utf-8") as logf:
        writer = csv.DictWriter(logf, fieldnames=["digest", "url", "status"])
        writer.writeheader()
        for row in log_rows:
            writer.writerow(row)
    print("\nBatch complete. Log written to", LOG_CSV)
    print("Summary:")
    print(f"  Total processed: {processed}")
    print(f"  Success: {success}")
    print(f"  Skipped (already exists): {skipped}")
    print(f"  Failed: {failed}")
    print("All HTML files are in:", os.path.abspath(HTML_OUT_DIR))


if __name__ == "__main__":
    main()
