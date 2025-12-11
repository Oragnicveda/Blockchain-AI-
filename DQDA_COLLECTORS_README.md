# DQDA Data Collectors Implementation

## Overview

This implementation provides modular data collectors under `agent/dqda/data_collectors/` for comprehensive startup due diligence data ingestion. Each collector follows the same design patterns, provides async-friendly interfaces, and normalizes outputs to a shared schema.

## Architecture

### Base Collector (`BaseCollector`)
Provides common functionality for all DQDA collectors:
- **Async-friendly interface** with `collect_data()` method
- **Exponential backoff retry** logic with configurable attempts
- **Shared schema** via `DQDADataPoint` class
- **Graceful degradation** when data sources are unavailable
- **Confidence scoring** and data quality assessment
- **Rate limiting** support for respectful data collection

### Shared Schema (`DQDADataPoint`)
All collectors normalize to this standardized structure:
```python
@dataclass
class DQDADataPoint:
    startup_name: str
    source_type: DataSource
    source_url: Optional[str]
    raw_content: Optional[str]
    structured_data: Dict[str, Any]
    collection_timestamp: datetime
    confidence_score: float
    data_quality_indicators: List[str]
    search_keywords: List[str]
    processing_notes: List[str]
```

## Collectors Implemented

### 1. Pitch Deck Parser (`PitchDeckParser`)
**Purpose**: Extract text and metadata from PDF pitch decks

**Features**:
- Multiple PDF parsing strategies (pdfplumber, PyPDF2, fallback)
- Metadata extraction (title, author, creation date)
- Section identification (problem, solution, market, team, financials)
- Quality assessment based on completeness and structure
- Startup relevance scoring

**Async Methods**:
- `collect_data()` - Main async interface
- `_download_pdf()` - Async PDF downloading
- `_extract_pdf_content()` - Async content extraction

### 2. Whitepaper Processor (`WhitepaperProcessor`)
**Purpose**: Process technical whitepapers with text cleaning and section tagging

**Features**:
- Multi-format support (PDF, HTML, TXT)
- Automatic section identification and tagging
- Technical terminology extraction by domain (blockchain, AI/ML, tech)
- Academic writing quality assessment
- Key insights extraction
- Domain-specific analysis (blockchain consensus, performance metrics)

**Async Methods**:
- `collect_data()` - Main async interface
- `_download_whitepaper()` - Async document downloading
- `_extract_and_clean_text()` - Async text processing

### 3. Website Crawler (`WebsiteCrawler`)
**Purpose**: Focused website scraping with robots.txt compliance

**Features**:
- Robots.txt compliance checking
- URL blacklisting and filtering
- Company information extraction (founded year, employees, funding, location)
- Team member identification (CEO, CTO, founder patterns)
- Site structure analysis and priority page detection
- Respectful crawling with rate limiting

**Async Methods**:
- `collect_data()` - Main async interface
- `_crawl_website()` - Async website crawling
- `_fetch_and_parse_page()` - Async page fetching

### 4. Tokenomics Collector (`TokenomicsCollector`)
**Purpose**: Query blockchain APIs for token economics data

**Features**:
- Multi-blockchain support (Ethereum, BSC, Polygon)
- Token supply metrics (total, circulating, max supply)
- Holder statistics and whale analysis
- Market data integration (price, volume, market cap)
- Contract verification and metadata
- Derived metrics calculation (inflation, concentration risk)

**Async Methods**:
- `collect_data()` - Main async interface
- `_collect_token_data()` - Async comprehensive data collection
- `_get_token_metadata()` - Async metadata fetching

### 5. Founder Background Collector (`FounderBackgroundCollector`)
**Purpose**: Collect founder and team background information

**Features**:
- LinkedIn profile search and analysis
- Professional experience extraction
- Educational background assessment
- Company network analysis
- Risk assessment based on background patterns
- Social media presence evaluation

**Async Methods**:
- `collect_data()` - Main async interface
- `_collect_founder_background()` - Async comprehensive background collection
- `_analyze_linkedin_profile()` - Async profile analysis

## Key Features

### Async-Friendly Design
All collectors support async operation for parallel execution:
```python
# Parallel execution example
tasks = [
    pitch_deck_parser.collect_data(startup_name, keywords),
    whitepaper_processor.collect_data(startup_name, keywords),
    website_crawler.collect_data(startup_name, keywords),
    tokenomics_collector.collect_data(startup_name, keywords),
    founder_collector.collect_data(startup_name, keywords)
]

results = await asyncio.gather(*tasks)
```

### Search-Based Collection
Each collector supports keyword-based search:
```python
data = await collector.collect_data(
    startup_name="StartupName",
    keywords=["blockchain", "defi", "fintech"],
    max_results=10
)
```

### Rate Limiting & Backoff
Built-in rate limiting and exponential backoff:
- Configurable delays between requests
- Exponential backoff on failures (1s, 2s, 4s, 8s...)
- Graceful handling of rate limit responses

### Error Handling & Recovery
Comprehensive error handling:
- Retry mechanisms with configurable attempts
- Graceful degradation when sources unavailable
- Detailed error logging and recovery
- Fallback to test/mock data for development

### Data Quality Assessment
Each collector provides confidence scoring:
- Based on data completeness and source reliability
- Quality indicators and processing notes
- Confidence scores from 0.0 to 1.0

## Configuration

### Environment Variables
```bash
# Rate limiting
RATE_LIMIT_DELAY=1.0

# Request timeout
REQUEST_TIMEOUT=30

# Max concurrent workers
MAX_WORKERS=5
```

### Custom Configuration
```python
# Custom rate limiting
crawler = WebsiteCrawler(rate_limit_delay=0.5)

# Custom blocked patterns
crawler.add_blocked_patterns([r'/beta.*', r'/test.*'])

# Custom priority paths
crawler.set_priority_paths({
    'about': ['/about', '/company', '/team'],
    'product': ['/product', '/solution']
})
```

## Testing

### Unit Tests (`test_dqda_collectors.py`)
Comprehensive test coverage with mocking:
- Base collector functionality tests
- Each collector's core methods tested
- Async method testing with mocks
- Error handling and graceful degradation
- Data quality and confidence scoring

### Demo Script (`dqda_demo.py`)
Interactive demonstration:
- Shows all collectors in action
- Parallel execution example
- Schema normalization demonstration
- Feature highlights and usage examples

### Running Tests
```bash
# Run all tests
python test_dqda_collectors.py

# Run demo
python dqda_demo.py
```

## Integration Example

```python
from agent.dqda.data_collectors import (
    PitchDeckParser,
    WhitepaperProcessor,
    WebsiteCrawler,
    TokenomicsCollector,
    FounderBackgroundCollector
)

async def comprehensive_startup_research(startup_name: str, keywords: List[str]):
    """Example comprehensive startup research using all collectors."""
    
    # Initialize all collectors
    collectors = [
        PitchDeckParser(),
        WhitepaperProcessor(),
        WebsiteCrawler(),
        TokenomicsCollector(),
        FounderBackgroundCollector()
    ]
    
    # Run all collectors in parallel
    tasks = [
        collector.collect_data(
            startup_name=startup_name,
            keywords=keywords,
            max_results=5
        )
        for collector in collectors
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Compile comprehensive report
    all_data_points = []
    for collector_results in results:
        all_data_points.extend(collector_results)
    
    # Normalize and analyze results
    high_confidence_data = [
        dp for dp in all_data_points 
        if dp.confidence_score > 0.7
    ]
    
    return {
        'startup_name': startup_name,
        'total_data_points': len(all_data_points),
        'high_confidence_points': len(high_confidence_data),
        'data_by_source': {
            source_type.value: [
                dp for dp in all_data_points 
                if dp.source_type == source_type
            ]
            for source_type in DataSource
        },
        'recommendations': generate_recommendations(high_confidence_data)
    }
```

## Dependencies

### Core Dependencies
- `requests>=2.31.0` - HTTP requests
- `beautifulsoup4>=4.12.0` - HTML parsing
- `pandas>=2.0.0` - Data manipulation

### PDF Processing
- `PyPDF2>=3.0.0` - PDF text extraction
- `pdfplumber>=0.9.0` - Advanced PDF processing

### Async Support
- `aiohttp>=3.9.0` - Async HTTP client
- `asyncio` - Python async framework

## Future Enhancements

1. **Additional Data Sources**:
   - Crunchbase API integration
   - AngelList profile scraping
   - GitHub repository analysis
   - Twitter/social media analysis

2. **Advanced Analytics**:
   - Machine learning for content classification
   - Sentiment analysis for founder profiles
   - Network analysis for connections
   - Predictive scoring models

3. **Performance Optimization**:
   - Caching layer implementation
   - Database integration
   - Batch processing optimization
   - Memory usage optimization

## Conclusion

The DQDA data collectors provide a robust, scalable, and modular foundation for startup due diligence data collection. Each collector can be used independently or combined for comprehensive analysis, with consistent interfaces and shared schemas enabling easy integration into larger research pipelines.