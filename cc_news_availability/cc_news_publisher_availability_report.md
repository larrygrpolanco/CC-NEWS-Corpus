# Common Crawl News Publisher Availability Report

## Summary

We conducted a comprehensive investigation to determine the availability of major US news publishers in the Common Crawl datasets (CC-MAIN and CC-NEWS). Our findings indicate that **none of the four major US news publishers we checked (Wall Street Journal, New York Times, Washington Post, and USA Today) are available in the Common Crawl datasets**.

## Methodology

Our investigation involved the following steps:

1. **Checking CC-MAIN dataset** using the CDX API for:
   - Wall Street Journal (wsj.com)
   - New York Times (nytimes.com)
   - Washington Post (washingtonpost.com)
   - USA Today (usatoday.com)

2. **Checking CC-NEWS dataset** by:
   - Examining the availability of WARC files from 2016 to 2024
   - Sampling WARC files from different years
   - Analyzing the content of these WARC files for the target publishers

3. **Checking robots.txt files** to understand why content might be missing

## Detailed Findings

### Wall Street Journal (wsj.com)
- No content found in CC-MAIN dataset (checked 2016-2024)
- No content found in CC-NEWS dataset (checked 2016-2024)
- WSJ's robots.txt explicitly blocks the Common Crawl bot:
  ```
  User-agent: CCBot
  Disallow: /
  ```

### New York Times (nytimes.com)
- No content found in CC-MAIN dataset (checked 2021-2025)
- Only robots.txt found in CC-MAIN-2025-13 (March 2025)
- No content found in CC-NEWS dataset (checked 2016-2024)

### Washington Post (washingtonpost.com)
- No content found in CC-MAIN dataset (checked 2016-2024)
- No content found in CC-NEWS dataset (checked 2016-2024)

### USA Today (usatoday.com)
- No content found in CC-MAIN dataset (checked 2016-2024)
- No content found in CC-NEWS dataset (checked 2016-2024)

## Alternative News Sources

While the major US news publishers are not available, we identified several other news sources in the CC-NEWS dataset that could potentially be used instead:

### International News Sources
1. news.sbs.co.kr (35 occurrences)
2. www.chinatimes.com (13 occurrences)
3. news.joins.com (11 occurrences)
4. hindi.news18.com (8 occurrences)
5. de.euronews.com (5 occurrences)

### US News Sources
1. www.darientimes.com (27 occurrences)
2. www.nydailynews.com (16 occurrences)
3. www.newsbreak.com (11 occurrences)
4. www.swtimes.com (10 occurrences)
5. www.srpressgazette.com (6 occurrences)

## Conclusions

1. **Major US news publishers block Common Crawl**: The evidence suggests that major US news publishers either actively block the Common Crawl bot through their robots.txt files or have had their content removed from the dataset.

2. **Alternative sources are available**: The CC-NEWS dataset contains a variety of other news sources, including international news outlets and smaller US news publications.

3. **Implications for corpus creation**: Creating a corpus of US political news articles from major publishers using Common Crawl data is not feasible. Alternative approaches would be needed, such as:
   - Using the alternative news sources identified in the CC-NEWS dataset
   - Exploring other public datasets of news articles
   - Considering direct licensing agreements with publishers (if budget allows)
   - Using smaller, regional US news sources that are available in the dataset

## Next Steps

Based on these findings, we recommend:

1. **Evaluate alternative news sources**: Assess the content and coverage of the alternative news sources identified in the CC-NEWS dataset to determine if they meet the project requirements.

2. **Consider scope adjustment**: Adjust the scope of the project to focus on news sources that are available in the Common Crawl datasets.

3. **Explore other datasets**: Investigate other public datasets that might contain news articles from major US publishers.
