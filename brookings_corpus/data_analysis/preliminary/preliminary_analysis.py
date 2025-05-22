#!/usr/bin/env python3
"""
Preliminary analysis of Brookings HTML corpus
Extracts metadata from brookings.dataLayer in HTML files and generates basic statistics
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import statistics

def extract_data_layer(html_content):
    """Extract brookings.dataLayer JSON from HTML content"""
    match = re.search(r'brookings\.dataLayer\s*=\s*({.*?});', html_content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
    return None

def analyze_files(input_dir):
    """Analyze all HTML files in directory"""
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'word_counts': [],
        'topics': defaultdict(int),
        'regions': defaultdict(int),
        'types': defaultdict(int),
        'years': defaultdict(int)
    }

    html_files = list(Path(input_dir).glob('*.html'))
    stats['total_files'] = len(html_files)

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                data = extract_data_layer(content)
                if data:
                    stats['processed_files'] += 1
                    if 'word_count' in data:
                        stats['word_counts'].append(data['word_count'])
                    stats['topics'][data.get('primary_topic', 'Unknown')] += 1
                    regions = data.get('region', 'Unknown')
                    if regions:
                        for region in [r.strip() for r in regions.split(',')]:
                            stats['regions'][region] += 1
                    else:
                        stats['regions']['Unknown'] += 1
                    stats['types'][data.get('type', 'Unknown')] += 1
                    year = data.get('yearPublished') or (data.get('publish_date', '')[:4] if data.get('publish_date') else 'Unknown')
                    stats['years'][year] += 1
                else:
                    print(f"No dataLayer found in {html_file}")
        except Exception as e:
            print(f"Error processing {html_file}: {str(e)}")
            continue

    if not stats['word_counts']:
        stats['word_counts'] = [0]  # Prevent empty list for statistics

    return stats

def generate_report(stats, output_file):
    """Generate a markdown report with enhanced statistics"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Brookings Corpus Preliminary Analysis Report\n\n")
        f.write(f"- **Total HTML files processed**: {stats['total_files']}\n")
        f.write(f"- **Successfully parsed**: {stats['processed_files']} ({stats['processed_files']/stats['total_files']:.1%})\n\n")
        
        f.write("## Word Count Statistics\n")
        f.write(f"- **Total words**: {sum(stats['word_counts']):,}\n")
        f.write(f"- **Average words per article**: {statistics.mean(stats['word_counts']):.1f}\n")
        f.write(f"- **Median words**: {statistics.median(stats['word_counts'])}\n")
        f.write(f"- **Shortest article**: {min(stats['word_counts'])} words\n")
        f.write(f"- **Longest article**: {max(stats['word_counts'])} words\n\n")
        
        f.write("## Content Distribution\n")
        f.write("### Top 10 Topics\n")
        for topic, count in sorted(stats['topics'].items(), key=lambda x: -x[1])[:10]:
            f.write(f"- {topic}: {count} ({count/stats['processed_files']:.1%})\n")
        
        f.write("\n### Article Types\n")
        for type_, count in sorted(stats['types'].items(), key=lambda x: -x[1]):
            f.write(f"- {type_}: {count} ({count/stats['processed_files']:.1%})\n")
        
        f.write("\n### Regions Covered\n")
        for region, count in sorted(stats['regions'].items(), key=lambda x: -x[1]):
            if region:  # Skip empty regions
                f.write(f"- {region}: {count} ({count/stats['processed_files']:.1%})\n")
        
        f.write("\n## Publication Timeline\n")
        f.write("| Year | Articles | Percentage |\n")
        f.write("|------|---------:|-----------:|\n")
        for year, count in sorted(stats['years'].items()):
            if year != 'Unknown':
                f.write(f"| {year} | {count} | {count/stats['processed_files']:.1%} |\n")

if __name__ == "__main__":
    input_dir = "html_raw"  # Relative to script location
    output_file = "brookings_corpus/data_analysis/preliminary/preliminary_report.md"  # Save in same directory as script

    print(f"Analyzing files in {input_dir}...")
    stats = analyze_files(input_dir)
    generate_report(stats, output_file)
    print(f"Analysis complete. Report saved to {output_file}")
