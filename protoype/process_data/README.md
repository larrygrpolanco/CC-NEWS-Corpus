# WARC Processor Module

## Purpose
This module provides basic functionality for processing WARC files from Common Crawl's CC-NEWS dataset.

## Features
- Filters WARC records by target domain
- Extracts article title and text
- Handles malformed HTML gracefully
- Returns structured article data

## Usage
```python

```


## The New York Times Politics URL format
Root https://www.nytimes.com/section/politics
article example https://www.nytimes.com/2025/05/16/us/politics/biden-audio-fitness-debate.html
date in format YYYY/MM/DD
title in kebab case
note: politics from this root is us specific which is fine for this project

## The Wall Street Journal Politics URL format
Root https://www.wsj.com/politics
The URL scheme of the WJS is not as easy to follow for just politics
Politics seems split into topics, but no topic is also an option
www.wsj.com/politics/elections/
www.wsj.com/politics/national-security/
www.wsj.com/politics/policy/

No date in URL
Articles are in kebabcase with some extra information at the end
ex. https://www.wsj.com/politics/policy/republican-tax-bill-conservative-demands-9ffeae23?mod=policy_news_article_pos3
ex. https://www.wsj.com/politics/i-thought-id-love-being-a-congressman-i-prefer-owning-a-bookshop-67f379a5?mod=politics_lead_story


## The Washington Post Politics URL format
Root https://www.washingtonpost.com/politics/
article example https://www.washingtonpost.com/politics/2025/05/16/biden-hur-audio-recording/
date in format YYYY/MM/DD
title in kebab case


## USA Today Politics URL format
Root https://www.usatoday.com/news/politics/
article example https://www.usatoday.com/story/news/politics/2025/05/16/trump-slams-taylor-swift-bruce-springsteen-supreme-court/83680151007/

Spanish Article
https://www.usatoday.com/story/news/politics/2025/05/16/corte-suprema-ciudadania-por-nacimiento-estados-unidos/83651898007/



Website format not as clear cut


## Dependencies
- warcio
- beautifulsoup4
- lxml

## Next Steps
- Add publisher-specific text extraction logic
- Add unit tests
