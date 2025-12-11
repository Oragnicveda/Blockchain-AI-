"""
DQDA (Due Diligence Data Aggregation) Data Collectors

Modular collectors for comprehensive startup due diligence data ingestion:
- Pitch deck parser (PDF extraction)
- Whitepaper processor (text cleaning and tagging)
- Website crawler (focused scraping with robots handling)
- Tokenomics collector (blockchain data APIs)
- Founder background collector (LinkedIn/profile search)

Each collector supports:
- Search-based mode (keyword + startup name)
- Async-friendly interfaces for parallelization
- Normalized output schema with confidence metrics
- Exponential backoff retries and graceful degradation
"""

from .base_collector import BaseCollector
from .pitch_deck_parser import PitchDeckParser
from .whitepaper_processor import WhitepaperProcessor
from .website_crawler import WebsiteCrawler
from .tokenomics_collector import TokenomicsCollector
from .founder_background_collector import FounderBackgroundCollector

__all__ = [
    'BaseCollector',
    'PitchDeckParser',
    'WhitepaperProcessor',
    'WebsiteCrawler',
    'TokenomicsCollector',
    'FounderBackgroundCollector'
]