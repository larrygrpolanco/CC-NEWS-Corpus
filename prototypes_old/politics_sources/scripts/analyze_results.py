#!/usr/bin/env python3
"""
Script to analyze availability and sample content results and generate a comprehensive report.
"""

import os
import sys
import json
import logging
import argparse
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_json_file(file_path):
    """
    Load a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: The loaded JSON data
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return None

def analyze_availability_results(availability_results):
    """
    Analyze availability results.
    
    Args:
        availability_results (list): List of availability results
        
    Returns:
        dict: Analysis of availability results
    """
    analysis = {
        'total_sources': len(availability_results),
        'available_sources': 0,
        'sources_with_articles': 0,
        'availability_by_type': defaultdict(lambda: {'total': 0, 'available': 0, 'with_articles': 0}),
        'availability_by_political_leaning': defaultdict(lambda: {'total': 0, 'available': 0}),
        'availability_by_geographic_focus': defaultdict(lambda: {'total': 0, 'available': 0}),
        'availability_by_crawl': defaultdict(int),
        'top_available_sources': []
    }
    
    # Analyze each source
    for result in availability_results:
        # Get basic info
        domain = result.get('domain', '')
        name = result.get('name', '')
        source_type = result.get('type', '')
        political_leaning = result.get('political_leaning', '')
        geographic_focus = result.get('geographic_focus', '')
        
        # Check availability
        overall_availability = result.get('overall_availability', {})
        availability_score = overall_availability.get('availability_score', 0)
        has_articles = overall_availability.get('has_articles', False)
        
        # Count available sources
        if availability_score > 0:
            analysis['available_sources'] += 1
            
            # Count sources with articles
            if has_articles:
                analysis['sources_with_articles'] += 1
        
        # Count by type
        analysis['availability_by_type'][source_type]['total'] += 1
        if availability_score > 0:
            analysis['availability_by_type'][source_type]['available'] += 1
            if has_articles:
                analysis['availability_by_type'][source_type]['with_articles'] += 1
        
        # Count by political leaning
        if political_leaning:
            analysis['availability_by_political_leaning'][political_leaning]['total'] += 1
            if availability_score > 0:
                analysis['availability_by_political_leaning'][political_leaning]['available'] += 1
        
        # Count by geographic focus
        if geographic_focus:
            analysis['availability_by_geographic_focus'][geographic_focus]['total'] += 1
            if availability_score > 0:
                analysis['availability_by_geographic_focus'][geographic_focus]['available'] += 1
        
        # Count by crawl
        for crawl_id, crawl_data in result.get('results', {}).items():
            if crawl_data.get('available', False) and not crawl_data.get('error', False):
                analysis['availability_by_crawl'][crawl_id] += 1
        
        # Add to top available sources if it has articles
        if has_articles and availability_score > 0:
            analysis['top_available_sources'].append({
                'domain': domain,
                'name': name,
                'type': source_type,
                'political_leaning': political_leaning,
                'geographic_focus': geographic_focus,
                'availability_score': availability_score,
                'has_articles': has_articles
            })
    
    # Sort top available sources by availability score
    analysis['top_available_sources'].sort(key=lambda x: x['availability_score'], reverse=True)
    
    # Convert defaultdicts to regular dicts for JSON serialization
    analysis['availability_by_type'] = dict(analysis['availability_by_type'])
    analysis['availability_by_political_leaning'] = dict(analysis['availability_by_political_leaning'])
    analysis['availability_by_geographic_focus'] = dict(analysis['availability_by_geographic_focus'])
    
    return analysis

def analyze_sample_results(sample_results):
    """
    Analyze sample content results.
    
    Args:
        sample_results (list): List of sample content results
        
    Returns:
        dict: Analysis of sample content results
    """
    analysis = {
        'total_sources': len(sample_results),
        'sources_with_samples': 0,
        'total_samples': 0,
        'content_types': Counter(),
        'extractability': {
            'easy': 0,
            'moderate': 0,
            'challenging': 0,
            'difficult': 0
        },
        'metadata_availability': {
            'title': 0,
            'author': 0,
            'date': 0,
            'section': 0
        },
        'content_structure': {
            'avg_paragraph_count': 0,
            'avg_word_count': 0,
            'has_images': 0,
            'has_links': 0,
            'has_blockquotes': 0,
            'has_lists': 0,
            'has_tables': 0,
            'has_iframes': 0
        },
        'top_extractable_sources': []
    }
    
    # Analyze each source
    sources_with_extractability = []
    total_samples_with_metadata = 0
    total_samples_with_content = 0
    
    for result in sample_results:
        samples_found = result.get('samples_found', 0)
        samples = result.get('samples', [])
        
        if samples_found > 0:
            analysis['sources_with_samples'] += 1
            analysis['total_samples'] += samples_found
            
            # Calculate extractability for this source
            extractability_scores = []
            for sample in samples:
                # Count content types
                content_type = sample.get('content_type', 'unknown')
                analysis['content_types'][content_type] += 1
                
                # Count extractability
                extractability = sample.get('extractability', 'difficult')
                analysis['extractability'][extractability] += 1
                
                # Convert extractability to score
                if extractability == 'easy':
                    extractability_scores.append(3)
                elif extractability == 'moderate':
                    extractability_scores.append(2)
                elif extractability == 'challenging':
                    extractability_scores.append(1)
                else:  # difficult
                    extractability_scores.append(0)
                
                # Count metadata availability
                metadata = sample.get('metadata', {})
                if metadata:
                    total_samples_with_metadata += 1
                    
                    if metadata.get('title', {}).get('found', False):
                        analysis['metadata_availability']['title'] += 1
                    
                    if metadata.get('author', {}).get('found', False):
                        analysis['metadata_availability']['author'] += 1
                    
                    if metadata.get('date', {}).get('found', False):
                        analysis['metadata_availability']['date'] += 1
                    
                    if metadata.get('section', {}).get('found', False):
                        analysis['metadata_availability']['section'] += 1
                
                # Count content structure
                content_structure = sample.get('content_structure', {})
                if content_structure and content_structure.get('content_found', False):
                    total_samples_with_content += 1
                    
                    analysis['content_structure']['avg_paragraph_count'] += content_structure.get('paragraph_count', 0)
                    analysis['content_structure']['avg_word_count'] += content_structure.get('word_count', 0)
                    
                    if content_structure.get('has_images', False):
                        analysis['content_structure']['has_images'] += 1
                    
                    if content_structure.get('has_links', False):
                        analysis['content_structure']['has_links'] += 1
                    
                    if content_structure.get('has_blockquotes', False):
                        analysis['content_structure']['has_blockquotes'] += 1
                    
                    if content_structure.get('has_lists', False):
                        analysis['content_structure']['has_lists'] += 1
                    
                    if content_structure.get('has_tables', False):
                        analysis['content_structure']['has_tables'] += 1
                    
                    if content_structure.get('has_iframes', False):
                        analysis['content_structure']['has_iframes'] += 1
            
            # Calculate average extractability score for this source
            if extractability_scores:
                avg_score = sum(extractability_scores) / len(extractability_scores)
                
                if avg_score >= 2.5:
                    difficulty = 'easy'
                elif avg_score >= 1.5:
                    difficulty = 'moderate'
                elif avg_score >= 0.5:
                    difficulty = 'challenging'
                else:
                    difficulty = 'difficult'
                
                sources_with_extractability.append({
                    'domain': result.get('domain', ''),
                    'name': result.get('name', ''),
                    'avg_score': avg_score,
                    'difficulty': difficulty
                })
    
    # Calculate averages for content structure
    if total_samples_with_content > 0:
        analysis['content_structure']['avg_paragraph_count'] /= total_samples_with_content
        analysis['content_structure']['avg_word_count'] /= total_samples_with_content
        
        # Convert counts to percentages
        for key in ['has_images', 'has_links', 'has_blockquotes', 'has_lists', 'has_tables', 'has_iframes']:
            analysis['content_structure'][key] = (analysis['content_structure'][key] / total_samples_with_content) * 100
    
    # Convert metadata counts to percentages
    if total_samples_with_metadata > 0:
        for key in analysis['metadata_availability']:
            analysis['metadata_availability'][key] = (analysis['metadata_availability'][key] / total_samples_with_metadata) * 100
    
    # Sort sources by extractability score
    sources_with_extractability.sort(key=lambda x: x['avg_score'], reverse=True)
    analysis['top_extractable_sources'] = sources_with_extractability[:20]  # Top 20
    
    return analysis

def generate_report(availability_analysis, sample_analysis, output_path):
    """
    Generate a comprehensive report based on the analyses.
    
    Args:
        availability_analysis (dict): Analysis of availability results
        sample_analysis (dict): Analysis of sample content results
        output_path (str): Path to save the report
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create report content
        report = []
        
        # Add title and introduction
        report.append("# Politics & International Relations Sources in Common Crawl")
        report.append("\n## Executive Summary")
        report.append("\nThis report presents the findings of an analysis of the availability and content quality of political and international relations sources in the Common Crawl dataset. The analysis focused on identifying sources that are well-represented in recent Common Crawl indexes and have extractable content suitable for corpus creation.")
        
        # Add availability summary
        report.append("\n## 1. Source Availability")
        report.append(f"\nOut of {availability_analysis['total_sources']} sources analyzed, {availability_analysis['available_sources']} ({availability_analysis['available_sources']/availability_analysis['total_sources']*100:.1f}%) were found to be available in at least one recent Common Crawl index. Of these, {availability_analysis['sources_with_articles']} ({availability_analysis['sources_with_articles']/availability_analysis['total_sources']*100:.1f}%) had identifiable article content.")
        
        # Add availability by crawl
        report.append("\n### 1.1 Availability by Crawl")
        report.append("\nThe following table shows the number of sources available in each Common Crawl index:")
        report.append("\n| Crawl ID | Available Sources | Percentage |")
        report.append("| --- | --- | --- |")
        for crawl_id, count in sorted(availability_analysis['availability_by_crawl'].items()):
            report.append(f"| {crawl_id} | {count} | {count/availability_analysis['total_sources']*100:.1f}% |")
        
        # Add availability by source type
        report.append("\n### 1.2 Availability by Source Type")
        report.append("\nThe following table shows the availability of sources by type:")
        report.append("\n| Source Type | Total | Available | With Articles | Availability % |")
        report.append("| --- | --- | --- | --- | --- |")
        for source_type, data in sorted(availability_analysis['availability_by_type'].items()):
            report.append(f"| {source_type} | {data['total']} | {data['available']} | {data['with_articles']} | {data['available']/data['total']*100 if data['total'] > 0 else 0:.1f}% |")
        
        # Add availability by political leaning
        report.append("\n### 1.3 Availability by Political Leaning")
        report.append("\nThe following table shows the availability of sources by political leaning:")
        report.append("\n| Political Leaning | Total | Available | Availability % |")
        report.append("| --- | --- | --- | --- |")
        for leaning, data in sorted(availability_analysis['availability_by_political_leaning'].items()):
            report.append(f"| {leaning} | {data['total']} | {data['available']} | {data['available']/data['total']*100 if data['total'] > 0 else 0:.1f}% |")
        
        # Add availability by geographic focus
        report.append("\n### 1.4 Availability by Geographic Focus")
        report.append("\nThe following table shows the availability of sources by geographic focus:")
        report.append("\n| Geographic Focus | Total | Available | Availability % |")
        report.append("| --- | --- | --- | --- |")
        for focus, data in sorted(availability_analysis['availability_by_geographic_focus'].items()):
            report.append(f"| {focus} | {data['total']} | {data['available']} | {data['available']/data['total']*100 if data['total'] > 0 else 0:.1f}% |")
        
        # Add top available sources
        report.append("\n### 1.5 Top Available Sources")
        report.append("\nThe following table shows the top 20 most available sources with article content:")
        report.append("\n| # | Name | Domain | Type | Political Leaning | Geographic Focus | Availability Score |")
        report.append("| --- | --- | --- | --- | --- | --- | --- |")
        for i, source in enumerate(availability_analysis['top_available_sources'][:20], 1):
            report.append(f"| {i} | {source['name']} | {source['domain']} | {source['type']} | {source['political_leaning']} | {source['geographic_focus']} | {source['availability_score']*100:.1f}% |")
        
        # Add sample analysis if available
        if sample_analysis:
            report.append("\n## 2. Content Analysis")
            report.append(f"\nA total of {sample_analysis['total_samples']} sample articles were analyzed from {sample_analysis['sources_with_samples']} sources. This section presents the findings of the content analysis.")
            
            # Add content types
            report.append("\n### 2.1 Content Types")
            report.append("\nThe following table shows the distribution of content types in the sample articles:")
            report.append("\n| Content Type | Count | Percentage |")
            report.append("| --- | --- | --- |")
            for content_type, count in sorted(sample_analysis['content_types'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"| {content_type} | {count} | {count/sample_analysis['total_samples']*100:.1f}% |")
            
            # Add extractability
            report.append("\n### 2.2 Content Extractability")
            report.append("\nThe following table shows the extractability of content from the sample articles:")
            report.append("\n| Extractability | Count | Percentage |")
            report.append("| --- | --- | --- |")
            total_extractability = sum(sample_analysis['extractability'].values())
            for difficulty, count in sorted(sample_analysis['extractability'].items(), key=lambda x: {'easy': 0, 'moderate': 1, 'challenging': 2, 'difficult': 3}[x[0]]):
                report.append(f"| {difficulty.capitalize()} | {count} | {count/total_extractability*100 if total_extractability > 0 else 0:.1f}% |")
            
            # Add metadata availability
            report.append("\n### 2.3 Metadata Availability")
            report.append("\nThe following table shows the availability of metadata in the sample articles:")
            report.append("\n| Metadata | Availability |")
            report.append("| --- | --- |")
            for metadata_type, percentage in sorted(sample_analysis['metadata_availability'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"| {metadata_type.capitalize()} | {percentage:.1f}% |")
            
            # Add content structure
            report.append("\n### 2.4 Content Structure")
            report.append("\nThe following table shows the average content structure of the sample articles:")
            report.append("\n| Metric | Value |")
            report.append("| --- | --- |")
            report.append(f"| Average Paragraph Count | {sample_analysis['content_structure']['avg_paragraph_count']:.1f} |")
            report.append(f"| Average Word Count | {sample_analysis['content_structure']['avg_word_count']:.1f} |")
            report.append(f"| Articles with Images | {sample_analysis['content_structure']['has_images']:.1f}% |")
            report.append(f"| Articles with Links | {sample_analysis['content_structure']['has_links']:.1f}% |")
            report.append(f"| Articles with Blockquotes | {sample_analysis['content_structure']['has_blockquotes']:.1f}% |")
            report.append(f"| Articles with Lists | {sample_analysis['content_structure']['has_lists']:.1f}% |")
            report.append(f"| Articles with Tables | {sample_analysis['content_structure']['has_tables']:.1f}% |")
            report.append(f"| Articles with Iframes | {sample_analysis['content_structure']['has_iframes']:.1f}% |")
            
            # Add top extractable sources
            report.append("\n### 2.5 Top Extractable Sources")
            report.append("\nThe following table shows the top 10 sources with the most extractable content:")
            report.append("\n| # | Name | Domain | Extractability | Score |")
            report.append("| --- | --- | --- | --- | --- |")
            for i, source in enumerate(sample_analysis['top_extractable_sources'][:10], 1):
                report.append(f"| {i} | {source['name']} | {source['domain']} | {source['difficulty'].capitalize()} | {source['avg_score']:.1f}/3 |")
        
        # Add recommendations
        report.append("\n## 3. Recommendations for Corpus Creation")
        
        # Combine top available and extractable sources
        top_sources = []
        if sample_analysis and sample_analysis['top_extractable_sources']:
            # Get domains of top extractable sources
            top_extractable_domains = [source['domain'] for source in sample_analysis['top_extractable_sources'][:10]]
            
            # Find these domains in top available sources
            for source in availability_analysis['top_available_sources']:
                if source['domain'] in top_extractable_domains:
                    top_sources.append({
                        'domain': source['domain'],
                        'name': source['name'],
                        'type': source['type'],
                        'political_leaning': source['political_leaning'],
                        'geographic_focus': source['geographic_focus'],
                        'availability_score': source['availability_score'],
                        'extractability': next((s['difficulty'] for s in sample_analysis['top_extractable_sources'] if s['domain'] == source['domain']), 'unknown')
                    })
        
        # If we don't have combined sources, just use top available
        if not top_sources:
            top_sources = availability_analysis['top_available_sources'][:10]
        
        report.append("\n### 3.1 Recommended Sources")
        report.append("\nBased on the analysis of availability and content quality, the following sources are recommended for inclusion in the corpus:")
        report.append("\n| # | Name | Domain | Type | Political Leaning | Geographic Focus | Availability | Extractability |")
        report.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for i, source in enumerate(top_sources[:10], 1):
            extractability = source.get('extractability', 'unknown')
            report.append(f"| {i} | {source['name']} | {source['domain']} | {source['type']} | {source['political_leaning']} | {source['geographic_focus']} | {source['availability_score']*100:.1f}% | {extractability.capitalize() if extractability != 'unknown' else 'Unknown'} |")
        
        # Add recommendations for corpus creation
        report.append("\n### 3.2 Corpus Creation Strategy")
        report.append("\nBased on the analysis, the following strategy is recommended for creating a corpus of political and international relations content from Common Crawl:")
        
        report.append("\n1. **Source Selection**: Focus on the recommended sources listed above, which have good availability in recent Common Crawl indexes and extractable content.")
        report.append("\n2. **Crawl Selection**: Use the most recent crawls (e.g., CC-MAIN-2025-18) for the most up-to-date content.")
        report.append("\n3. **Content Extraction**:")
        report.append("   - Use metadata extraction techniques to identify article title, author, date, and section.")
        report.append("   - Extract the main content using the identified content containers.")
        report.append("   - Handle special content elements like images, blockquotes, and lists as needed.")
        
        report.append("\n4. **Corpus Organization**:")
        report.append("   - Organize the corpus by source, date, and potentially by topic or section.")
        report.append("   - Create a metadata file with information about each article, including source, author, date, URL, and extraction details.")
        
        report.append("\n5. **Quality Control**:")
        report.append("   - Implement validation checks to ensure the extracted content is complete and accurate.")
        report.append("   - Manually review a sample of extracted articles to verify extraction quality.")
        
        # Add research considerations
        report.append("\n### 3.3 Research Considerations")
        report.append("\nWhen using this corpus for research on persuasive language in political and international relations content, consider the following:")
        
        report.append("\n1. **Source Diversity**: The corpus includes sources with different political leanings and geographic focuses, allowing for comparative analysis of persuasive language across these dimensions.")
        
        report.append("\n2. **Content Types**: The corpus includes different types of content (articles, opinion pieces, analysis, etc.), which may employ different persuasive strategies.")
        
        report.append("\n3. **Temporal Analysis**: The corpus can be used to analyze changes in persuasive language over time, particularly around significant events.")
        
        report.append("\n4. **Metadata Utilization**: The metadata (author, date, section) can be used as variables in the analysis to identify patterns in persuasive language use.")
        
        report.append("\n5. **Limitations**: Be aware of the limitations of the corpus, including potential biases in source selection and content extraction.")
        
        # Add conclusion
        report.append("\n## 4. Conclusion")
        report.append("\nThis analysis has identified a set of political and international relations sources that are well-represented in recent Common Crawl indexes and have extractable content suitable for corpus creation. By following the recommended strategy, a high-quality corpus can be created for research on persuasive language in political and international relations content.")
        
        report.append("\nThe corpus will enable research on how persuasive language varies across different types of sources, political leanings, and geographic focuses, as well as how it changes over time in response to significant events.")
        
        # Write report to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))
        
        logger.info(f"Report generated and saved to {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return False

def main():
    """
    Main function to analyze results and generate a report.
    """
    parser = argparse.ArgumentParser(description='Analyze availability and sample content results')
    parser.add_argument('--availability-file', type=str, required=True,
                        help='Path to the availability results JSON file')
    parser.add_argument('--sample-file', type=str, default=None,
                        help='Path to the sample analysis JSON file (optional)')
    parser.add_argument('--output-dir', type=str, default='../reports',
                        help='Directory to save the report')
    args = parser.parse_args()
    
    # Resolve paths relative to the script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    availability_path = os.path.abspath(os.path.join(script_dir, args.availability_file))
    sample_path = os.path.abspath(os.path.join(script_dir, args.sample_file)) if args.sample_file else None
    output_dir = os.path.abspath(os.path.join(script_dir, args.output_dir))
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load availability results
    availability_results = load_json_file(availability_path)
    if not availability_results:
        logger.error(f"Failed to load availability results from {availability_path}")
        return
    
    # Load sample results if provided
    sample_results = None
    if sample_path:
        sample_results = load_json_file(sample_path)
        if not sample_results:
            logger.warning(f"Failed to load sample results from {sample_path}")
    
    # Analyze results
    availability_analysis = analyze_availability_results(availability_results)
    sample_analysis = analyze_sample_results(sample_results) if sample_results else None
    
    # Generate timestamp for output files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate report
    report_path = os.path.join(output_dir, f'availability_report_{timestamp}.md')
    success = generate_report(availability_analysis, sample_analysis, report_path)
    
    if success:
        print(f"\nReport generated successfully and saved to {report_path}")
    else:
        print("\nFailed to generate report")

if __name__ == "__main__":
    main()
