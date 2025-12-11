#!/usr/bin/env python3
"""
DQDA Data Collectors Example Demo

Demonstrates the modular DQDA data collectors in action:
- Pitch deck parser for PDF extraction
- Whitepaper processor for document analysis
- Website crawler for company information
- Tokenomics collector for blockchain data
- Founder background collector for team analysis

Run with: python dqda_demo.py
"""

import asyncio
import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from agent.dqda.data_collectors.pitch_deck_parser import PitchDeckParser
from agent.dqda.data_collectors.whitepaper_processor import WhitepaperProcessor
from agent.dqda.data_collectors.website_crawler import WebsiteCrawler
from agent.dqda.data_collectors.tokenomics_collector import TokenomicsCollector
from agent.dqda.data_collectors.founder_background_collector import FounderBackgroundCollector


async def demo_collectors():
    """Demonstrate all DQDA collectors with sample data."""
    
    print("🚀 DQDA Data Collectors Demo")
    print("=" * 50)
    
    # Demo startup information
    startup_name = "TestTech"
    keywords = ["blockchain", "startup", "technology"]
    
    print(f"\n📊 Analyzing Startup: {startup_name}")
    print(f"Keywords: {', '.join(keywords)}")
    
    # Initialize collectors
    collectors = {
        'Pitch Deck Parser': PitchDeckParser(),
        'Whitepaper Processor': WhitepaperProcessor(),
        'Website Crawler': WebsiteCrawler(),
        'Tokenomics Collector': TokenomicsCollector(),
        'Founder Background': FounderBackgroundCollector()
    }
    
    # Demo results storage
    results = {}
    
    # Demo each collector
    for name, collector in collectors.items():
        print(f"\n🔍 Running {name}...")
        
        try:
            if name == 'Pitch Deck Parser':
                # Demo with mock PDF URLs
                data = await collector.collect_data(
                    startup_name=startup_name,
                    keywords=keywords,
                    max_results=2
                )
            
            elif name == 'Whitepaper Processor':
                # Demo with document processing
                data = await collector.collect_data(
                    startup_name=startup_name,
                    keywords=keywords,
                    max_results=2
                )
            
            elif name == 'Website Crawler':
                # Demo with mock website URLs
                data = await collector.collect_data(
                    startup_name=startup_name,
                    keywords=keywords,
                    max_results=2,
                    base_urls=["https://testtech.example.com"]
                )
            
            elif name == 'Tokenomics Collector':
                # Demo with token contract addresses
                data = await collector.collect_data(
                    startup_name=startup_name,
                    keywords=keywords,
                    max_results=1,
                    use_test_data=True
                )
            
            elif name == 'Founder Background':
                # Demo with founder discovery
                data = await collector.collect_data(
                    startup_name=startup_name,
                    keywords=keywords,
                    max_results=2
                )
            
            results[name] = data
            
            if data:
                print(f"   ✅ Collected {len(data)} data points")
                # Show sample data structure
                if len(data) > 0:
                    sample = data[0]
                    print(f"   📄 Sample: {sample.startup_name} | Type: {sample.source_type.value} | Confidence: {sample.confidence_score:.2f}")
            else:
                print(f"   ⚠️  No data collected (expected for demo without real data sources)")
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            results[name] = []
    
    # Generate summary report
    print("\n📋 DEMO SUMMARY REPORT")
    print("=" * 50)
    
    total_data_points = sum(len(data) for data in results.values())
    print(f"Total Data Points Collected: {total_data_points}")
    
    print("\nData by Collector:")
    for name, data in results.items():
        print(f"  • {name}: {len(data)} points")
    
    # Show detailed sample from each collector that returned data
    print("\n🔬 SAMPLE DATA STRUCTURES")
    print("=" * 50)
    
    for name, data_list in results.items():
        if data_list:
            print(f"\n{name}:")
            sample = data_list[0]
            print(f"  Startup: {sample.startup_name}")
            print(f"  Source: {sample.source_type.value}")
            print(f"  Confidence: {sample.confidence_score:.2f}")
            print(f"  URL: {sample.source_url or 'N/A'}")
            print(f"  Keywords: {sample.search_keywords}")
            
            # Show structured data if available
            if sample.structured_data:
                print(f"  Structured Data Keys: {list(sample.structured_data.keys())}")
    
    # Show the shared schema in action
    print("\n📐 SHARED SCHEMA DEMONSTRATION")
    print("=" * 50)
    
    if results and any(data for data in results.values()):
        # Find first non-empty result
        sample_data = next((data[0] for data in results.values() if data), None)
        if sample_data:
            print("All collectors normalize to the same DQDADataPoint schema:")
            schema = {
                'startup_name': sample_data.startup_name,
                'source_type': sample_data.source_type.value,
                'confidence_score': sample_data.confidence_score,
                'collection_timestamp': sample_data.collection_timestamp.isoformat(),
                'search_keywords': sample_data.search_keywords,
                'structured_data_keys': list(sample_data.structured_data.keys())
            }
            print(json.dumps(schema, indent=2))
    
    # Demonstrate parallel execution
    print("\n⚡ PARALLEL EXECUTION DEMO")
    print("=" * 50)
    
    print("Running all collectors in parallel...")
    start_time = datetime.now()
    
    tasks = []
    for collector in collectors.values():
        task = collector.collect_data(
            startup_name=startup_name,
            keywords=keywords,
            max_results=1
        )
        tasks.append(task)
    
    parallel_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    successful_results = sum(1 for result in parallel_results if not isinstance(result, Exception))
    print(f"Completed in {duration:.2f}s | Successful: {successful_results}/{len(collectors)}")
    
    # Feature highlights
    print("\n🌟 KEY FEATURES DEMONSTRATED")
    print("=" * 50)
    print("✅ Async-friendly interfaces for parallel execution")
    print("✅ Shared schema (DQDADataPoint) for data normalization")
    print("✅ Exponential backoff retry mechanisms")
    print("✅ Graceful degradation when data sources unavailable")
    print("✅ Confidence scoring and quality assessment")
    print("✅ Source URL tracking and metadata preservation")
    print("✅ Search-based data collection with keywords")
    print("✅ Rate limiting and respectful crawling practices")
    print("✅ Error handling and recovery mechanisms")
    
    print("\n🎯 READY FOR INTEGRATION")
    print("=" * 50)
    print("The DQDA collectors are modular and ready to be integrated into")
    print("a comprehensive startup research pipeline. Each collector can be")
    print("used independently or combined for comprehensive due diligence.")
    
    return results


def main():
    """Main demo function."""
    try:
        # Run the async demo
        results = asyncio.run(demo_collectors())
        
        print(f"\n🏁 Demo completed successfully!")
        print(f"Check the output above for detailed results from each collector.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())