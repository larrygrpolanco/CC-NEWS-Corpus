import csv
from collections import defaultdict, namedtuple
import os

# Configurable parameters
MERGE_THRESHOLD = 1024 * 1024  # 1MB: merge ranges within this many bytes
FULL_WARC_THRESHOLD = 0.5      # If merged ranges cover >50% of file, recommend full download

# Placeholder: user should replace with actual file size lookup if available
# For real use, you may want to fetch WARC file sizes from S3 or a manifest
WARC_FILE_SIZES = {}

Record = namedtuple('Record', ['offset', 'length', 'url'])

def read_csv(input_csv):
    warc_map = defaultdict(list)
    with open(input_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row['filename']
            offset = int(row['offset'])
            length = int(row['length'])
            url = row.get('url', '')
            warc_map[filename].append(Record(offset, length, url))
    return warc_map

def merge_ranges(records, threshold=MERGE_THRESHOLD):
    # records: list of Record, sorted by offset
    merged = []
    if not records:
        return merged
    current_start = records[0].offset
    current_end = records[0].offset + records[0].length
    current_urls = [records[0].url]
    for rec in records[1:]:
        if rec.offset <= current_end + threshold:
            # Merge
            current_end = max(current_end, rec.offset + rec.length)
            current_urls.append(rec.url)
        else:
            merged.append((current_start, current_end, list(current_urls)))
            current_start = rec.offset
            current_end = rec.offset + rec.length
            current_urls = [rec.url]
    merged.append((current_start, current_end, list(current_urls)))
    return merged

def plan_downloads(warc_map):
    plan = []
    for filename, records in warc_map.items():
        records = sorted(records, key=lambda r: r.offset)
        merged_ranges = merge_ranges(records)
        # Placeholder: assume WARC file size is max end offset + 1MB
        warc_size = max(r.offset + r.length for r in records) + 1024 * 1024
        if filename in WARC_FILE_SIZES:
            warc_size = WARC_FILE_SIZES[filename]
        total_merged_bytes = sum(end - start for start, end, _ in merged_ranges)
        if total_merged_bytes / warc_size > FULL_WARC_THRESHOLD or len(merged_ranges) > 20:
            plan.append({
                'filename': filename,
                'download_type': 'full',
                'ranges': '',
                'num_records': len(records),
                'num_merged_ranges': len(merged_ranges)
            })
        else:
            for start, end, urls in merged_ranges:
                plan.append({
                    'filename': filename,
                    'download_type': 'range',
                    'ranges': f'{start}-{end-1}',
                    'num_records': len(urls),
                    'num_merged_ranges': 1
                })
    return plan

def write_plan_csv(plan, output_csv):
    fieldnames = ['filename', 'download_type', 'ranges', 'num_records', 'num_merged_ranges']
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in plan:
            writer.writerow(row)

def main():
    input_csv = os.path.join(
        os.path.dirname(__file__),
        "brookings_cdx_working_sample.csv",
    )
    output_csv = os.path.join(os.path.dirname(__file__), 'warc_download_plan.csv')
    warc_map = read_csv(input_csv)
    plan = plan_downloads(warc_map)
    write_plan_csv(plan, output_csv)
    print(f"Download plan written to {output_csv}")
    print("Summary:")
    for row in plan:
        print(row)

if __name__ == '__main__':
    main()
