"""
Base collector for DQDA data ingestion module.

Provides common functionality for all DQDA collectors including:
- Shared data schema and normalization
- Async-friendly interface
- Exponential backoff retries
- Confidence scoring
- Graceful degradation
"""

import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from agent.utils.logger import setup_logger
from agent.utils.config import Config

logger = setup_logger(__name__)


class DataSource(Enum):
    """Enumeration of supported data sources."""
    PITCH_DECK = "pitch_deck"
    WHITEPAPER = "whitepaper"
    WEBSITE = "website"
    TOKENOMICS = "tokenomics"
    FOUNDER_PROFILE = "founder_profile"


class ConfidenceLevel(Enum):
    """Data confidence levels."""
    HIGH = 0.9
    MEDIUM = 0.7
    LOW = 0.5
    VERY_LOW = 0.3


@dataclass
class DQDADataPoint:
    """
    Standardized data point for all DQDA collectors.
    
    This is the shared schema that all collectors should normalize their outputs to.
    """
    # Core identification
    startup_name: str
    source_type: DataSource
    source_url: Optional[str] = None
    
    # Content data
    raw_content: Optional[str] = None
    structured_data: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    collection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = 0.5
    data_quality_indicators: List[str] = field(default_factory=list)
    
    # Processing metadata
    processing_notes: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    retry_count: int = 0
    
    # Search context
    search_keywords: List[str] = field(default_factory=list)
    search_startup_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'startup_name': self.startup_name,
            'source_type': self.source_type.value,
            'source_url': self.source_url,
            'raw_content': self.raw_content,
            'structured_data': self.structured_data,
            'collection_timestamp': self.collection_timestamp.isoformat(),
            'confidence_score': self.confidence_score,
            'data_quality_indicators': self.data_quality_indicators,
            'processing_notes': self.processing_notes,
            'errors': self.errors,
            'retry_count': self.retry_count,
            'search_keywords': self.search_keywords,
            'search_startup_name': self.search_startup_name,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DQDADataPoint':
        """Create from dictionary."""
        data['collection_timestamp'] = datetime.fromisoformat(data['collection_timestamp'].replace('Z', '+00:00'))
        data['source_type'] = DataSource(data['source_type'])
        return cls(**data)


class BaseCollector(ABC):
    """
    Base class for all DQDA data collectors.
    
    Provides common functionality for:
    - Async operation support
    - Exponential backoff retries
    - Data normalization to shared schema
    - Search-based data collection
    - Graceful degradation
    """
    
    def __init__(self, rate_limit_delay: Optional[float] = None):
        self.config = Config()
        self.rate_limit_delay = rate_limit_delay or self.config.RATE_LIMIT_DELAY
        self.max_retries = 3
        self.base_delay = 1.0
        
    async def collect_data(
        self,
        startup_name: str,
        keywords: List[str],
        max_results: int = 10,
        **kwargs
    ) -> List[DQDADataPoint]:
        """
        Async interface for data collection.
        
        Args:
            startup_name: Name of the startup to research
            keywords: Keywords related to the startup
            max_results: Maximum number of results to collect
            **kwargs: Additional collector-specific parameters
            
        Returns:
            List of normalized data points
        """
        logger.info(f"Starting data collection for {startup_name} using {self.__class__.__name__}")
        
        try:
            # Create search context
            search_context = {
                'startup_name': startup_name,
                'keywords': keywords,
                'max_results': max_results,
                **kwargs
            }
            
            # Perform data collection
            raw_data = await self._collect_raw_data(**search_context)
            
            # Normalize to shared schema
            normalized_data = []
            for item in raw_data:
                try:
                    normalized = self._normalize_data(item, startup_name, keywords)
                    if normalized:
                        normalized_data.append(normalized)
                        await asyncio.sleep(self.rate_limit_delay)  # Rate limiting
                except Exception as e:
                    logger.warning(f"Error normalizing data item: {str(e)}")
                    continue
            
            logger.info(f"Collected {len(normalized_data)} data points for {startup_name}")
            return normalized_data[:max_results]
            
        except Exception as e:
            logger.error(f"Error in data collection for {startup_name}: {str(e)}")
            return self._graceful_degradation(startup_name, keywords, str(e))
    
    @abstractmethod
    async def _collect_raw_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Abstract method for raw data collection.
        
        Each collector implements its specific data gathering logic here.
        
        Returns:
            List of raw data dictionaries
        """
        pass
    
    def _normalize_data(
        self,
        raw_data: Dict[str, Any],
        startup_name: str,
        keywords: List[str]
    ) -> Optional[DQDADataPoint]:
        """
        Normalize raw data to the shared DQDA schema.
        
        Args:
            raw_data: Raw data from collector
            startup_name: Startup name for context
            keywords: Search keywords for context
            
        Returns:
            Normalized DQDADataPoint or None if normalization fails
        """
        try:
            # Default confidence score based on data completeness
            confidence = self._calculate_confidence_score(raw_data)
            
            # Extract source URL if available
            source_url = raw_data.get('url') or raw_data.get('source_url') or raw_data.get('link')
            
            # Create normalized data point
            data_point = DQDADataPoint(
                startup_name=startup_name,
                source_type=self._get_source_type(),
                source_url=source_url,
                raw_content=raw_data.get('content') or raw_data.get('text') or raw_data.get('data'),
                structured_data=self._extract_structured_data(raw_data),
                confidence_score=confidence,
                data_quality_indicators=self._assess_data_quality(raw_data),
                search_keywords=keywords,
                search_startup_name=startup_name,
                processing_notes=self._generate_processing_notes(raw_data)
            )
            
            return data_point
            
        except Exception as e:
            logger.warning(f"Error normalizing data: {str(e)}")
            return None
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All retry attempts failed: {str(e)}")
        
        return None
    
    def _calculate_confidence_score(self, raw_data: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the data based on completeness and quality indicators.
        
        Args:
            raw_data: Raw data to assess
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.5  # Base score
        
        # Increase score for completeness
        if raw_data.get('content') or raw_data.get('text'):
            score += 0.2
        if raw_data.get('url') or raw_data.get('source_url'):
            score += 0.1
        if raw_data.get('metadata'):
            score += 0.1
        if raw_data.get('title'):
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_structured_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from raw data for storage in structured_data field.
        
        Args:
            raw_data: Raw data dictionary
            
        Returns:
            Structured data dictionary
        """
        # Remove non-structured fields
        exclude_fields = {'content', 'text', 'data', 'url', 'source_url', 'link', 'html'}
        structured = {k: v for k, v in raw_data.items() if k not in exclude_fields}
        
        return structured
    
    def _assess_data_quality(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Assess data quality and return quality indicators.
        
        Args:
            raw_data: Raw data to assess
            
        Returns:
            List of quality indicators
        """
        indicators = []
        
        if raw_data.get('content') and len(raw_data['content']) > 100:
            indicators.append('substantial_content')
        if raw_data.get('url'):
            indicators.append('has_source_url')
        if raw_data.get('metadata'):
            indicators.append('has_metadata')
        if raw_data.get('title'):
            indicators.append('has_title')
        
        return indicators
    
    def _generate_processing_notes(self, raw_data: Dict[str, Any]) -> List[str]:
        """
        Generate processing notes for the data collection.
        
        Args:
            raw_data: Raw data being processed
            
        Returns:
            List of processing notes
        """
        notes = [f"Collected via {self.__class__.__name__}"]
        
        if raw_data.get('collection_method'):
            notes.append(f"Method: {raw_data['collection_method']}")
        
        return notes
    
    def _graceful_degradation(
        self,
        startup_name: str,
        keywords: List[str],
        error_msg: str
    ) -> List[DQDADataPoint]:
        """
        Provide graceful degradation when data collection fails.
        
        Args:
            startup_name: Startup name
            keywords: Search keywords
            error_msg: Error message that caused degradation
            
        Returns:
            List containing a single data point with error information
        """
        return [DQDADataPoint(
            startup_name=startup_name,
            source_type=self._get_source_type(),
            confidence_score=0.1,
            errors=[error_msg],
            processing_notes=[f"Graceful degradation for {self.__class__.__name__}"],
            search_keywords=keywords,
            search_startup_name=startup_name
        )]
    
    @abstractmethod
    def _get_source_type(self) -> DataSource:
        """
        Get the data source type for this collector.
        
        Returns:
            DataSource enum value
        """
        pass
    
    def get_search_suggestions(self, startup_name: str) -> List[str]:
        """
        Get search suggestions for a given startup name.
        
        Args:
            startup_name: Name of the startup
            
        Returns:
            List of search suggestion strings
        """
        base_suggestions = [
            f"{startup_name} company",
            f"{startup_name} official website",
            f"{startup_name} pitch deck",
            f"{startup_name} whitepaper"
        ]
        
        return base_suggestions