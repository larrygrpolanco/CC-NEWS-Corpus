import requests
import json
import time

def check_cc_main_for_wsj(crawl_id):
    """Check if WSJ politics URLs are in a specific CC-MAIN crawl."""
    url = f"https://index.commoncrawl.org/{crawl_id}-index?url=wsj.com/politics&output=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        if "No Captures found" in response.text:
            return False, "No captures found"
        else:
            return True, response.text
    else:
        return False, f"Error: {response.status_code} - {response.text}"

def check_cc_main_for_wsj_robots(crawl_id):
    """Check if WSJ robots.txt is in a specific CC-MAIN crawl."""
    url = f"https://index.commoncrawl.org/{crawl_id}-index?url=wsj.com/robots.txt&output=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        if "No Captures found" in response.text:
            return False, "No captures found"
        else:
            return True, response.text
    else:
        return False, f"Error: {response.status_code} - {response.text}"

def check_cc_main_for_wsj_domain(crawl_id):
    """Check if WSJ domain is in a specific CC-MAIN crawl."""
    url = f"https://index.commoncrawl.org/{crawl_id}-index?url=wsj.com&output=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        if "No Captures found" in response.text:
            return False, "No captures found"
        else:
            return True, response.text
    else:
        return False, f"Error: {response.status_code} - {response.text}"

def get_available_crawls():
    """Get a list of available CC-MAIN crawls."""
    url = "http://index.commoncrawl.org/collinfo.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return []

# Get available crawls
crawls = get_available_crawls()
print(f"Found {len(crawls)} available crawls")

# Check the most recent crawls for WSJ politics URLs
for crawl in crawls[:10]:  # Check the 10 most recent crawls
    crawl_id = crawl["id"]
    print(f"\nChecking {crawl_id} ({crawl['name']})...")
    
    # Check for WSJ politics URLs
    print("Checking for WSJ politics URLs...")
    found, result = check_cc_main_for_wsj(crawl_id)
    if found:
        print(f"Found WSJ politics URLs in {crawl_id}!")
        print(result[:500])  # Print first 500 chars of result
    else:
        print(f"No WSJ politics URLs found in {crawl_id}: {result}")
    
    # Check for WSJ domain
    print("Checking for WSJ domain...")
    found, result = check_cc_main_for_wsj_domain(crawl_id)
    if found:
        print(f"Found WSJ domain in {crawl_id}!")
        print(result[:500])  # Print first 500 chars of result
    else:
        print(f"No WSJ domain found in {crawl_id}: {result}")
    
    # Check for WSJ robots.txt
    print("Checking for WSJ robots.txt...")
    found, result = check_cc_main_for_wsj_robots(crawl_id)
    if found:
        print(f"Found WSJ robots.txt in {crawl_id}!")
        print(result[:500])  # Print first 500 chars of result
    else:
        print(f"No WSJ robots.txt found in {crawl_id}: {result}")
    
    # Sleep to avoid rate limiting
    time.sleep(1)
