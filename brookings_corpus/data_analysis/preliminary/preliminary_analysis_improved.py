#!/usr/bin/env python3
"""
Improved preliminary analysis of Brookings HTML corpus
Extracts comprehensive metadata from brookings.dataLayer in HTML files and generates detailed statistics
"""

import json
import re
from pathlib import Path
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

def clean_field(value):
    """Clean and normalize field values"""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        return value if value else None
    return value

def parse_multiple_values(value, separator=','):
    """Parse comma-separated values into a list"""
    if not value:
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]

def analyze_files(input_dir):
    """Analyze all HTML files in directory with comprehensive metadata extraction"""
    stats = {
        'total_files': 0,
        'processed_files': 0,
        'missing_datalayer': 0,
        'word_counts': [],
        'topics': defaultdict(int),
        'regions': defaultdict(int),
        'types': defaultdict(int),
        'content_types': defaultdict(int),
        'combined_types': defaultdict(int),  # type + content_type combinations
        'programs': defaultdict(int),
        'centers': defaultdict(int),
        'projects': defaultdict(int),
        'author_types': defaultdict(int),
        'years': defaultdict(int),
        'data_quality': {
            'has_region': 0,
            'has_program': 0,
            'has_center': 0,
            'has_project': 0,
            'has_type': 0,
            'has_content_type': 0,
            'has_primary_topic': 0
        }
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
                    
                    # Word count
                    word_count = data.get('word_count')
                    if word_count and isinstance(word_count, (int, float)):
                        stats['word_counts'].append(int(word_count))
                    
                    # Topics
                    primary_topic = clean_field(data.get('primary_topic'))
                    if primary_topic:
                        stats['topics'][primary_topic] += 1
                        stats['data_quality']['has_primary_topic'] += 1
                    else:
                        stats['topics']['[No Primary Topic]'] += 1
                    
                    # Multiple topics from 'topic' field
                    topic_field = clean_field(data.get('topic'))
                    if topic_field:
                        for topic in parse_multiple_values(topic_field):
                            stats['topics'][f"Secondary: {topic}"] += 1
                    
                    # Regions - distinguish between missing and intentionally empty
                    region_field = data.get('region')
                    if region_field is None:
                        stats['regions']['[Missing Data]'] += 1
                    elif region_field == '':
                        stats['regions']['[No Regional Focus]'] += 1
                    else:
                        stats['data_quality']['has_region'] += 1
                        for region in parse_multiple_values(region_field):
                            stats['regions'][region] += 1
                    
                    # Types and Content Types
                    article_type = clean_field(data.get('type'))
                    content_type = clean_field(data.get('content_type'))
                    
                    if article_type:
                        stats['types'][article_type] += 1
                        stats['data_quality']['has_type'] += 1
                    else:
                        stats['types']['[No Type]'] += 1
                    
                    if content_type:
                        stats['content_types'][content_type] += 1
                        stats['data_quality']['has_content_type'] += 1
                    else:
                        stats['content_types']['[No Content Type]'] += 1
                    
                    # Combined type classification
                    if article_type and content_type:
                        combined = f"{content_type} - {article_type}"
                    elif content_type:
                        combined = content_type
                    elif article_type:
                        combined = article_type
                    else:
                        combined = "[Unclassified]"
                    stats['combined_types'][combined] += 1
                    
                    # Institutional context
                    program = clean_field(data.get('program'))
                    if program:
                        stats['programs'][program] += 1
                        stats['data_quality']['has_program'] += 1
                    else:
                        stats['programs']['[No Program]'] += 1
                    
                    center = clean_field(data.get('center'))
                    if center:
                        stats['centers'][center] += 1
                        stats['data_quality']['has_center'] += 1
                    else:
                        stats['centers']['[No Center]'] += 1
                    
                    project = clean_field(data.get('project'))
                    if project:
                        stats['projects'][project] += 1
                        stats['data_quality']['has_project'] += 1
                    else:
                        stats['projects']['[No Project]'] += 1
                    
                    # Author types
                    author_type = clean_field(data.get('author_type'))
                    if author_type:
                        for auth_type in parse_multiple_values(author_type):
                            stats['author_types'][auth_type] += 1
                    else:
                        stats['author_types']['[Unknown]'] += 1
                    
                    # Years
                    year = data.get('yearPublished') or (data.get('publish_date', '')[:4] if data.get('publish_date') else None)
                    if year and str(year).isdigit():
                        stats['years'][str(year)] += 1
                    else:
                        stats['years']['[Unknown Year]'] += 1
                        
                else:
                    stats['missing_datalayer'] += 1
                    print(f"No dataLayer found in {html_file}")
                    
        except Exception as e:
            print(f"Error processing {html_file}: {str(e)}")
            continue

    # Ensure we have word counts for statistics
    if not stats['word_counts']:
        stats['word_counts'] = [0]

    return stats

def generate_enhanced_report(stats, output_file):
    """Generate a comprehensive markdown report"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Brookings Corpus Enhanced Preliminary Analysis Report\n\n")
        
        # Overview
        f.write("## Overview\n")
        f.write(f"- **Total HTML files processed**: {stats['total_files']:,}\n")
        f.write(f"- **Successfully parsed**: {stats['processed_files']:,} ({stats['processed_files']/stats['total_files']:.1%})\n")
        f.write(f"- **Missing dataLayer**: {stats['missing_datalayer']:,} ({stats['missing_datalayer']/stats['total_files']:.1%})\n\n")
        
        # Data Quality Assessment
        f.write("## Data Quality Assessment\n")
        total_processed = stats['processed_files']
        if total_processed > 0:
            f.write(f"- **Articles with regional focus**: {stats['data_quality']['has_region']:,} ({stats['data_quality']['has_region']/total_processed:.1%})\n")
            f.write(f"- **Articles with program assignment**: {stats['data_quality']['has_program']:,} ({stats['data_quality']['has_program']/total_processed:.1%})\n")
            f.write(f"- **Articles with center assignment**: {stats['data_quality']['has_center']:,} ({stats['data_quality']['has_center']/total_processed:.1%})\n")
            f.write(f"- **Articles with project assignment**: {stats['data_quality']['has_project']:,} ({stats['data_quality']['has_project']/total_processed:.1%})\n")
            f.write(f"- **Articles with type classification**: {stats['data_quality']['has_type']:,} ({stats['data_quality']['has_type']/total_processed:.1%})\n")
            f.write(f"- **Articles with content type**: {stats['data_quality']['has_content_type']:,} ({stats['data_quality']['has_content_type']/total_processed:.1%})\n")
            f.write(f"- **Articles with primary topic**: {stats['data_quality']['has_primary_topic']:,} ({stats['data_quality']['has_primary_topic']/total_processed:.1%})\n\n")
        
        # Word Count Statistics
        f.write("## Word Count Statistics\n")
        if stats['word_counts'] and max(stats['word_counts']) > 0:
            f.write(f"- **Total words**: {sum(stats['word_counts']):,}\n")
            f.write(f"- **Average words per article**: {statistics.mean(stats['word_counts']):.1f}\n")
            f.write(f"- **Median words**: {statistics.median(stats['word_counts']):.0f}\n")
            f.write(f"- **Shortest article**: {min(stats['word_counts']):,} words\n")
            f.write(f"- **Longest article**: {max(stats['word_counts']):,} words\n\n")
        
        # Content Classification
        f.write("## Content Classification\n")
        
        f.write("### Combined Type Classification (Content Type + Article Type)\n")
        for combined_type, count in sorted(stats['combined_types'].items(), key=lambda x: -x[1])[:15]:
            f.write(f"- **{combined_type}**: {count:,} ({count/total_processed:.1%})\n")
        
        f.write("\n### Content Types\n")
        for content_type, count in sorted(stats['content_types'].items(), key=lambda x: -x[1]):
            f.write(f"- **{content_type}**: {count:,} ({count/total_processed:.1%})\n")
        
        f.write("\n### Article Types\n")
        for article_type, count in sorted(stats['types'].items(), key=lambda x: -x[1]):
            f.write(f"- **{article_type}**: {count:,} ({count/total_processed:.1%})\n")
        
        # Topics
        f.write("\n## Topic Analysis\n")
        f.write("### Top 15 Primary Topics\n")
        primary_topics = {k: v for k, v in stats['topics'].items() if not k.startswith('Secondary:')}
        for topic, count in sorted(primary_topics.items(), key=lambda x: -x[1])[:15]:
            f.write(f"- **{topic}**: {count:,} ({count/total_processed:.1%})\n")
        
        # Regional Coverage
        f.write("\n## Regional Coverage\n")
        f.write("### Top 20 Regions\n")
        for region, count in sorted(stats['regions'].items(), key=lambda x: -x[1])[:20]:
            f.write(f"- **{region}**: {count:,} ({count/total_processed:.1%})\n")
        
        # Institutional Context
        f.write("\n## Institutional Context\n")
        
        f.write("### Top 10 Programs\n")
        for program, count in sorted(stats['programs'].items(), key=lambda x: -x[1])[:10]:
            f.write(f"- **{program}**: {count:,} ({count/total_processed:.1%})\n")
        
        f.write("\n### Top 10 Centers\n")
        for center, count in sorted(stats['centers'].items(), key=lambda x: -x[1])[:10]:
            f.write(f"- **{center}**: {count:,} ({count/total_processed:.1%})\n")
        
        f.write("\n### Author Types\n")
        for author_type, count in sorted(stats['author_types'].items(), key=lambda x: -x[1]):
            f.write(f"- **{author_type}**: {count:,} ({count/total_processed:.1%})\n")
        
        # Publication Timeline
        f.write("\n## Publication Timeline\n")
        f.write("| Year | Articles | Percentage |\n")
        f.write("|------|---------:|-----------:|\n")
        for year, count in sorted(stats['years'].items()):
            if year != '[Unknown Year]' and year.isdigit():
                f.write(f"| {year} | {count:,} | {count/total_processed:.1%} |\n")
        
        # Research Insights
        f.write("\n## Research Insights for Diachronic Analysis\n")
        f.write("### Content Evolution Patterns\n")
        commentary_count = stats['content_types'].get('Commentary', 0)
        research_count = stats['content_types'].get('Research', 0)
        f.write(f"- **Commentary vs Research ratio**: {commentary_count:,} Commentary ({commentary_count/total_processed:.1%}) vs {research_count:,} Research ({research_count/total_processed:.1%})\n")
        
        regional_focus = stats['data_quality']['has_region']
        f.write(f"- **Articles with regional focus**: {regional_focus:,} ({regional_focus/total_processed:.1%}) - suitable for geographic linguistic analysis\n")
        
        program_coverage = stats['data_quality']['has_program']
        f.write(f"- **Articles with program assignment**: {program_coverage:,} ({program_coverage/total_processed:.1%}) - enables policy domain analysis\n")

if __name__ == "__main__":
    input_dir = "html_raw"  # Relative to script location
    output_file = "brookings_corpus/data_analysis/preliminary/enhanced_preliminary_report.md"

    print(f"Analyzing files in {input_dir}...")
    stats = analyze_files(input_dir)
    generate_enhanced_report(stats, output_file)
    print(f"Enhanced analysis complete. Report saved to {output_file}")
    
    # Print quick summary
    print(f"\nQuick Summary:")
    print(f"- Processed {stats['processed_files']:,} articles from {stats['total_files']:,} files")
    print(f"- Content types: {len([k for k in stats['content_types'].keys() if not k.startswith('[')])} distinct types")
    print(f"- Regional coverage: {stats['data_quality']['has_region']:,} articles ({stats['data_quality']['has_region']/stats['processed_files']:.1%})")
    print(f"- Program assignment: {stats['data_quality']['has_program']:,} articles ({stats['data_quality']['has_program']/stats['processed_files']:.1%})")
