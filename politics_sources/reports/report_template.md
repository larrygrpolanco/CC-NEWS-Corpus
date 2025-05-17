# Politics & International Relations Sources in Common Crawl

## Executive Summary

This report presents the findings of an analysis of the availability and content quality of political and international relations sources in the Common Crawl dataset. The analysis focused on identifying sources that are well-represented in recent Common Crawl indexes and have extractable content suitable for corpus creation.

## 1. Source Availability

Out of [TOTAL_SOURCES] sources analyzed, [AVAILABLE_SOURCES] ([AVAILABLE_PERCENTAGE]%) were found to be available in at least one recent Common Crawl index. Of these, [SOURCES_WITH_ARTICLES] ([ARTICLES_PERCENTAGE]%) had identifiable article content.

### 1.1 Availability by Crawl

The following table shows the number of sources available in each Common Crawl index:

| Crawl ID | Available Sources | Percentage |
| --- | --- | --- |
| [CRAWL_ID_1] | [COUNT_1] | [PERCENTAGE_1]% |
| [CRAWL_ID_2] | [COUNT_2] | [PERCENTAGE_2]% |
| ... | ... | ... |

### 1.2 Availability by Source Type

The following table shows the availability of sources by type:

| Source Type | Total | Available | With Articles | Availability % |
| --- | --- | --- | --- | --- |
| [TYPE_1] | [TOTAL_1] | [AVAILABLE_1] | [WITH_ARTICLES_1] | [PERCENTAGE_1]% |
| [TYPE_2] | [TOTAL_2] | [AVAILABLE_2] | [WITH_ARTICLES_2] | [PERCENTAGE_2]% |
| ... | ... | ... | ... | ... |

### 1.3 Availability by Political Leaning

The following table shows the availability of sources by political leaning:

| Political Leaning | Total | Available | Availability % |
| --- | --- | --- | --- |
| [LEANING_1] | [TOTAL_1] | [AVAILABLE_1] | [PERCENTAGE_1]% |
| [LEANING_2] | [TOTAL_2] | [AVAILABLE_2] | [PERCENTAGE_2]% |
| ... | ... | ... | ... |

### 1.4 Availability by Geographic Focus

The following table shows the availability of sources by geographic focus:

| Geographic Focus | Total | Available | Availability % |
| --- | --- | --- | --- |
| [FOCUS_1] | [TOTAL_1] | [AVAILABLE_1] | [PERCENTAGE_1]% |
| [FOCUS_2] | [TOTAL_2] | [AVAILABLE_2] | [PERCENTAGE_2]% |
| ... | ... | ... | ... |

### 1.5 Top Available Sources

The following table shows the top 20 most available sources with article content:

| # | Name | Domain | Type | Political Leaning | Geographic Focus | Availability Score |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [NAME_1] | [DOMAIN_1] | [TYPE_1] | [LEANING_1] | [FOCUS_1] | [SCORE_1]% |
| 2 | [NAME_2] | [DOMAIN_2] | [TYPE_2] | [LEANING_2] | [FOCUS_2] | [SCORE_2]% |
| ... | ... | ... | ... | ... | ... | ... |

## 2. Content Analysis

A total of [TOTAL_SAMPLES] sample articles were analyzed from [SOURCES_WITH_SAMPLES] sources. This section presents the findings of the content analysis.

### 2.1 Content Types

The following table shows the distribution of content types in the sample articles:

| Content Type | Count | Percentage |
| --- | --- | --- |
| [TYPE_1] | [COUNT_1] | [PERCENTAGE_1]% |
| [TYPE_2] | [COUNT_2] | [PERCENTAGE_2]% |
| ... | ... | ... |

### 2.2 Content Extractability

The following table shows the extractability of content from the sample articles:

| Extractability | Count | Percentage |
| --- | --- | --- |
| Easy | [COUNT_EASY] | [PERCENTAGE_EASY]% |
| Moderate | [COUNT_MODERATE] | [PERCENTAGE_MODERATE]% |
| Challenging | [COUNT_CHALLENGING] | [PERCENTAGE_CHALLENGING]% |
| Difficult | [COUNT_DIFFICULT] | [PERCENTAGE_DIFFICULT]% |

### 2.3 Metadata Availability

The following table shows the availability of metadata in the sample articles:

| Metadata | Availability |
| --- | --- |
| Title | [TITLE_PERCENTAGE]% |
| Author | [AUTHOR_PERCENTAGE]% |
| Date | [DATE_PERCENTAGE]% |
| Section | [SECTION_PERCENTAGE]% |

### 2.4 Content Structure

The following table shows the average content structure of the sample articles:

| Metric | Value |
| --- | --- |
| Average Paragraph Count | [AVG_PARAGRAPH_COUNT] |
| Average Word Count | [AVG_WORD_COUNT] |
| Articles with Images | [IMAGES_PERCENTAGE]% |
| Articles with Links | [LINKS_PERCENTAGE]% |
| Articles with Blockquotes | [BLOCKQUOTES_PERCENTAGE]% |
| Articles with Lists | [LISTS_PERCENTAGE]% |
| Articles with Tables | [TABLES_PERCENTAGE]% |
| Articles with Iframes | [IFRAMES_PERCENTAGE]% |

### 2.5 Top Extractable Sources

The following table shows the top 10 sources with the most extractable content:

| # | Name | Domain | Extractability | Score |
| --- | --- | --- | --- | --- |
| 1 | [NAME_1] | [DOMAIN_1] | [EXTRACTABILITY_1] | [SCORE_1]/3 |
| 2 | [NAME_2] | [DOMAIN_2] | [EXTRACTABILITY_2] | [SCORE_2]/3 |
| ... | ... | ... | ... | ... |

## 3. Recommendations for Corpus Creation

### 3.1 Recommended Sources

Based on the analysis of availability and content quality, the following sources are recommended for inclusion in the corpus:

| # | Name | Domain | Type | Political Leaning | Geographic Focus | Availability | Extractability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | [NAME_1] | [DOMAIN_1] | [TYPE_1] | [LEANING_1] | [FOCUS_1] | [AVAILABILITY_1]% | [EXTRACTABILITY_1] |
| 2 | [NAME_2] | [DOMAIN_2] | [TYPE_2] | [LEANING_2] | [FOCUS_2] | [AVAILABILITY_2]% | [EXTRACTABILITY_2] |
| ... | ... | ... | ... | ... | ... | ... | ... |

### 3.2 Corpus Creation Strategy

Based on the analysis, the following strategy is recommended for creating a corpus of political and international relations content from Common Crawl:

1. **Source Selection**: Focus on the recommended sources listed above, which have good availability in recent Common Crawl indexes and extractable content.

2. **Crawl Selection**: Use the most recent crawls (e.g., CC-MAIN-2025-18) for the most up-to-date content.

3. **Content Extraction**:
   - Use metadata extraction techniques to identify article title, author, date, and section.
   - Extract the main content using the identified content containers.
   - Handle special content elements like images, blockquotes, and lists as needed.

4. **Corpus Organization**:
   - Organize the corpus by source, date, and potentially by topic or section.
   - Create a metadata file with information about each article, including source, author, date, URL, and extraction details.

5. **Quality Control**:
   - Implement validation checks to ensure the extracted content is complete and accurate.
   - Manually review a sample of extracted articles to verify extraction quality.

### 3.3 Research Considerations

When using this corpus for research on persuasive language in political and international relations content, consider the following:

1. **Source Diversity**: The corpus includes sources with different political leanings and geographic focuses, allowing for comparative analysis of persuasive language across these dimensions.

2. **Content Types**: The corpus includes different types of content (articles, opinion pieces, analysis, etc.), which may employ different persuasive strategies.

3. **Temporal Analysis**: The corpus can be used to analyze changes in persuasive language over time, particularly around significant events.

4. **Metadata Utilization**: The metadata (author, date, section) can be used as variables in the analysis to identify patterns in persuasive language use.

5. **Limitations**: Be aware of the limitations of the corpus, including potential biases in source selection and content extraction.

## 4. Conclusion

This analysis has identified a set of political and international relations sources that are well-represented in recent Common Crawl indexes and have extractable content suitable for corpus creation. By following the recommended strategy, a high-quality corpus can be created for research on persuasive language in political and international relations content.

The corpus will enable research on how persuasive language varies across different types of sources, political leanings, and geographic focuses, as well as how it changes over time in response to significant events.
