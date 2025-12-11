# DQDA Collectors Integration Guide

## Quick Start

```python
from agent.dqda.data_collectors import (
    PitchDeckParser, WhitepaperProcessor, WebsiteCrawler,
    TokenomicsCollector, FounderBackgroundCollector
)

# Initialize collectors
collectors = [
    PitchDeckParser(),
    WhitepaperProcessor(), 
    WebsiteCrawler(),
    TokenomicsCollector(),
    FounderBackgroundCollector()
]

# Run comprehensive research
async def research_startup(startup_name: str, keywords: list):
    tasks = [
        collector.collect_data(
            startup_name=startup_name,
            keywords=keywords, 
            max_results=5
        )
        for collector in collectors
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Execute
results = asyncio.run(research_startup("ExampleCorp", ["ai", "blockchain"]))
```

## File Structure Created

```
agent/dqda/data_collectors/
├── __init__.py                    # Exports all collectors
├── base_collector.py              # Base class with shared functionality
├── pitch_deck_parser.py           # PDF extraction and analysis
├── whitepaper_processor.py        # Document processing and tagging
├── website_crawler.py             # Website scraping with robots.txt
├── tokenomics_collector.py        # Blockchain data collection
└── founder_background_collector.py # Team background analysis

test_dqda_collectors.py           # Comprehensive test suite with mocks
dqda_demo.py                     # Interactive demonstration script
DQDA_COLLECTORS_README.md        # Detailed documentation
requirements.txt                 # Updated with PDF processing deps
```

## Key Features Implemented

✅ **Modular Architecture**: Each collector is independent and reusable
✅ **Async-Friendly**: Full async support for parallel execution  
✅ **Shared Schema**: All outputs normalized to DQDADataPoint format
✅ **Search-Based**: Keyword + startup name search patterns
✅ **Rate Limiting**: Configurable delays and respectful crawling
✅ **Error Recovery**: Exponential backoff + graceful degradation
✅ **Quality Scoring**: Confidence metrics and data quality assessment
✅ **Test Coverage**: Unit tests with mocks for all collectors

## Testing

```bash
# Run test suite
python test_dqda_collectors.py

# Run demo
python dqda_demo.py
```

The implementation is production-ready and follows enterprise patterns for reliability, scalability, and maintainability.