import requests
import gzip
import io
from warcio.archiveiterator import ArchiveIterator

def fetch_robots_txt_from_warc(warc_url, offset, length):
    """Fetch a robots.txt file from a WARC file."""
    # Define the byte range for the request
    byte_range = f'bytes={offset}-{int(offset)+int(length)-1}'
    
    # Send the HTTP GET request to the S3 URL with the specified byte range
    response = requests.get(
        f"https://data.commoncrawl.org/{warc_url}",
        headers={'Range': byte_range},
        stream=True
    )
    
    if response.status_code == 206:  # Partial Content
        # Create an ArchiveIterator object from the response content
        stream = ArchiveIterator(response.raw)
        for record in stream:
            # Return the content of the record
            return record.content_stream().read()
    else:
        return f"Error: {response.status_code} - {response.text}"

# Use the robots.txt from CC-MAIN-2025-08 (February 2025) which had a 200 status
warc_url = "crawl-data/CC-MAIN-2025-08/segments/1738831951398.56/robotstxt/CC-MAIN-20250206114225-20250206144225-00816.warc.gz"
offset = "1821416"
length = "2029"

robots_txt_content = fetch_robots_txt_from_warc(warc_url, offset, length)
print(robots_txt_content)
