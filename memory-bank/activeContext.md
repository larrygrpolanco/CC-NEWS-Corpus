# Active Context: CC-NEWS Corpus Project

## Current Task (2025-05-17)
Determine the availability of major US news publishers in the Common Crawl CC-NEWS dataset.
**Status: Checked for Wall Street Journal, New York Times, Washington Post, and USA Today content in CC-NEWS dataset from 2016 to 2024. None of these publishers' content was found. The Wall Street Journal's robots.txt explicitly blocks the Common Crawl bot (CCBot).**

## Previous Task (2025-05-17)
Determine the latest Common Crawl index that contains articles from The New York Times (nytimes.com).
**Status: Searched CC-MAIN crawls from March 2025 back to Nov/Dec 2021. No NYT articles found. Only `nytimes.com/robots.txt` (which disallows CCBot) was found in CC-MAIN-2025-13 (March 2025). All other checked CC-MAIN crawls showed "No Captures found for: nytimes.com/".**

## User Request
- Initially, check for New York Times content in Common Crawl.
- After finding that NYT content was not available, pivot to checking for Wall Street Journal content.
- Check for other major US news publishers (Washington Post, USA Today) as alternatives.

## Information Gathered
- Reviewed `CC_docs/`.
- Checked CC-MAIN crawls for NYT content using CDX API - none found.
- Checked CC-NEWS dataset for WSJ, NYT, Washington Post, and USA Today content - none found.
- Found that WSJ's robots.txt explicitly blocks the Common Crawl bot (CCBot).
- Identified other news sources available in CC-NEWS dataset, including:
  - International news sources: news.sbs.co.kr, www.chinatimes.com, news.joins.com
  - Smaller US news sources: www.darientimes.com, www.nydailynews.com, www.swtimes.com

## Next Steps
- Consider using alternative news sources found in the CC-NEWS dataset.
- Explore other potential sources for news articles outside of Common Crawl.
- Potentially focus on smaller or international news sources that are available in the CC-NEWS dataset.

## Key Considerations
- Major US news publishers (WSJ, NYT, Washington Post, USA Today) appear to block the Common Crawl bot or have had their content removed from the dataset.
- The CC-NEWS dataset contains a variety of other news sources that could be used instead.
- Need to decide whether to proceed with alternative news sources or explore other data sources entirely.
