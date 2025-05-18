import json
import csv

INPUT_FILE = "brookings_cdx_matches.txt"
CSV_OUTPUT = "brookings_cdx_matches.csv"
WORKING_SAMPLE_OUTPUT = "brookings_cdx_working_sample.csv"

def parse_line(line):
    # Each line: [SURT_URL] [timestamp] [JSON]
    try:
        parts = line.strip().split(" ", 2)
        if len(parts) != 3:
            return None
        surt_url, timestamp, json_str = parts
        meta = json.loads(json_str)
        return surt_url, timestamp, meta
    except Exception:
        return None

def get_all_json_fields(input_path):
    # Collect all possible JSON keys for CSV header
    fields = set()
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_line(line)
            if parsed:
                _, _, meta = parsed
                fields.update(meta.keys())
    return sorted(fields)

def main():
    json_fields = get_all_json_fields(INPUT_FILE)
    csv_fields = ["surt_url", "timestamp"] + json_fields

    with open(INPUT_FILE, "r", encoding="utf-8") as infile, \
         open(CSV_OUTPUT, "w", newline="", encoding="utf-8") as csvfile, \
         open(WORKING_SAMPLE_OUTPUT, "w", newline="", encoding="utf-8") as samplefile:

        writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
        writer.writeheader()

        sample_writer = csv.DictWriter(samplefile, fieldnames=csv_fields)
        sample_writer.writeheader()

        for line in infile:
            parsed = parse_line(line)
            if not parsed:
                continue
            surt_url, timestamp, meta = parsed

            row = {k: meta.get(k, "") for k in json_fields}
            row["surt_url"] = surt_url
            row["timestamp"] = timestamp

            writer.writerow(row)

            # Working sample logic
            status = str(meta.get("status", ""))
            url = meta.get("url", "")
            languages = meta.get("languages", "")
            if (status == "200" and languages == "eng"):
                sample_writer.writerow(row)
            elif (status == "301" and languages == "eng" and url.startswith("https://www.brookings.edu/articles/")):
                sample_writer.writerow(row)
            # All others are excluded

if __name__ == "__main__":
    main()
