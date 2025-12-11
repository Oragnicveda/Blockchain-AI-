"""
Pitch deck parser for DQDA data collection.

Extracts text and metadata from PDF pitch decks with:
- PDF text extraction using multiple parsing strategies
- Metadata extraction (title, author, creation date)
- Confidence scoring based on text quality and completeness
- Support for common pitch deck file patterns
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from agent.utils.logger import setup_logger
from agent.dqda.data_collectors.base_collector import BaseCollector, DataSource, DQDADataPoint

logger = setup_logger(__name__)

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available, will use fallback parsing")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available, will use fallback parsing")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available, remote PDF fetching disabled")


class PitchDeckParser(BaseCollector):
    """
    Parser for PDF pitch decks with text and metadata extraction.
    
    Supports:
    - Multiple PDF parsing libraries with fallback
    - Remote PDF fetching from URLs
    - Local file processing
    - Metadata extraction and text quality assessment
    - Pitch deck section identification
    """
    
    def __init__(self):
        super().__init__()
        self.session = None
        if REQUESTS_AVAILABLE:
            import requests
            self.session = requests.Session()
            # Set up common headers for PDF requests
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
    
    async def _collect_raw_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect pitch deck data from multiple sources.
        
        Expected kwargs:
            startup_name: Name of the startup
            keywords: List of keywords for search
            max_results: Maximum number of results
            pdf_urls: Optional list of direct PDF URLs
            search_domains: Optional list of domains to search
        """
        startup_name = kwargs.get('startup_name', '')
        keywords = kwargs.get('keywords', [])
        max_results = kwargs.get('max_results', 5)
        pdf_urls = kwargs.get('pdf_urls', [])
        
        results = []
        
        # Process provided PDF URLs first
        if pdf_urls:
            for url in pdf_urls[:max_results]:
                data = await self._extract_from_url(url, startup_name, keywords)
                if data:
                    results.append(data)
                    if len(results) >= max_results:
                        break
        
        # Search for additional pitch decks if needed
        if len(results) < max_results:
            search_urls = await self._search_for_pitch_decks(startup_name, keywords, max_results - len(results))
            for url in search_urls:
                data = await self._extract_from_url(url, startup_name, keywords)
                if data:
                    results.append(data)
                    if len(results) >= max_results:
                        break
        
        return results
    
    async def _extract_from_url(self, url: str, startup_name: str, keywords: List[str]) -> Optional[Dict[str, Any]]:
        """
        Extract pitch deck data from a PDF URL.
        
        Args:
            url: URL of the PDF
            startup_name: Name of the startup
            keywords: Search keywords
            
        Returns:
            Raw data dictionary or None if extraction fails
        """
        try:
            logger.info(f"Extracting pitch deck from: {url}")
            
            # Download PDF
            pdf_content = await self._download_pdf(url)
            if not pdf_content:
                return None
            
            # Extract text and metadata
            extraction_result = await self._extract_pdf_content(pdf_content)
            if not extraction_result:
                return None
            
            # Enhance with pitch deck specific analysis
            enhanced_result = self._analyze_pitch_deck_content(extraction_result, startup_name)
            
            return {
                'url': url,
                'content': enhanced_result['text'],
                'metadata': enhanced_result['metadata'],
                'sections': enhanced_result['sections'],
                'quality_indicators': enhanced_result['quality_indicators'],
                'collection_method': 'pdf_extraction',
                'startup_name': startup_name,
                'search_keywords': keywords
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF from {url}: {str(e)}")
            return None
    
    async def _download_pdf(self, url: str) -> Optional[bytes]:
        """
        Download PDF content from URL.
        
        Args:
            url: URL to download from
            
        Returns:
            PDF content as bytes or None if download fails
        """
        if not self.session:
            logger.warning("No session available for PDF download")
            return None
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.session.get(url, timeout=30)
            )
            response.raise_for_status()
            
            # Basic PDF validation
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"URL doesn't appear to be a PDF: {url}")
                return None
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error downloading PDF from {url}: {str(e)}")
            return None
    
    async def _extract_pdf_content(self, pdf_content: bytes) -> Optional[Dict[str, Any]]:
        """
        Extract text and metadata from PDF content using available libraries.
        
        Args:
            pdf_content: PDF content as bytes
            
        Returns:
            Dictionary with extracted text and metadata or None
        """
        try:
            # Try pdfplumber first (usually better for text extraction)
            if PDFPLUMBER_AVAILABLE:
                return await self._extract_with_pdfplumber(pdf_content)
            elif PDF_AVAILABLE:
                return await self._extract_with_pypdf2(pdf_content)
            else:
                logger.error("No PDF extraction libraries available")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            return None
    
    async def _extract_with_pdfplumber(self, pdf_content: bytes) -> Optional[Dict[str, Any]]:
        """Extract using pdfplumber library."""
        import pdfplumber
        
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._pdfplumber_extraction,
                pdf_content
            )
            return result
            
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            return None
    
    def _pdfplumber_extraction(self, pdf_content: bytes) -> Dict[str, Any]:
        """Execute pdfplumber extraction in thread pool."""
        import pdfplumber
        
        extracted_text = []
        metadata = {}
        page_count = 0
        
        with pdfplumber.open(pdf_content) as pdf:
            page_count = len(pdf.pages)
            
            # Extract metadata
            if pdf.metadata:
                metadata = {
                    'title': pdf.metadata.get('/Title', ''),
                    'author': pdf.metadata.get('/Author', ''),
                    'subject': pdf.metadata.get('/Subject', ''),
                    'creator': pdf.metadata.get('/Creator', ''),
                    'producer': pdf.metadata.get('/Producer', ''),
                    'creation_date': str(pdf.metadata.get('/CreationDate', '')),
                    'modification_date': str(pdf.metadata.get('/ModDate', ''))
                }
            
            # Extract text from each page
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
        
        full_text = '\n'.join(extracted_text)
        
        return {
            'text': full_text,
            'metadata': metadata,
            'page_count': page_count,
            'extraction_method': 'pdfplumber'
        }
    
    async def _extract_with_pypdf2(self, pdf_content: bytes) -> Optional[Dict[str, Any]]:
        """Extract using PyPDF2 library."""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._pypdf2_extraction,
                pdf_content
            )
            return result
            
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            return None
    
    def _pypdf2_extraction(self, pdf_content: bytes) -> Dict[str, Any]:
        """Execute PyPDF2 extraction in thread pool."""
        import PyPDF2
        
        import io
        extracted_text = []
        metadata = {}
        page_count = 0
        
        pdf_stream = io.BytesIO(pdf_content)
        
        with PyPDF2.PdfReader(pdf_stream) as pdf:
            page_count = len(pdf.pages)
            
            # Extract metadata
            if pdf.metadata:
                metadata = {
                    'title': pdf.metadata.get('/Title', ''),
                    'author': pdf.metadata.get('/Author', ''),
                    'subject': pdf.metadata.get('/Subject', ''),
                    'creator': pdf.metadata.get('/Creator', ''),
                    'producer': pdf.metadata.get('/Producer', ''),
                    'creation_date': str(pdf.metadata.get('/CreationDate', '')),
                    'modification_date': str(pdf.metadata.get('/ModDate', ''))
                }
            
            # Extract text from each page
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
        
        full_text = '\n'.join(extracted_text)
        
        return {
            'text': full_text,
            'metadata': metadata,
            'page_count': page_count,
            'extraction_method': 'pypdf2'
        }
    
    def _analyze_pitch_deck_content(self, extraction_result: Dict[str, Any], startup_name: str) -> Dict[str, Any]:
        """
        Analyze pitch deck content for startup-relevant sections and quality indicators.
        
        Args:
            extraction_result: Result from PDF extraction
            startup_name: Name of the startup
            
        Returns:
            Enhanced analysis results
        """
        text = extraction_result['text']
        metadata = extraction_result['metadata']
        
        # Identify pitch deck sections
        sections = self._identify_pitch_deck_sections(text)
        
        # Quality indicators
        quality_indicators = self._assess_pitch_deck_quality(text, metadata, sections)
        
        # Startup relevance
        relevance_score = self._calculate_startup_relevance(text, startup_name)
        
        # Update metadata with analysis
        enhanced_metadata = metadata.copy()
        enhanced_metadata.update({
            'startup_relevance_score': relevance_score,
            'section_count': len(sections),
            'quality_score': sum(quality_indicators.values()) / len(quality_indicators) if quality_indicators else 0.0,
            'analysis_date': str(extraction_result.get('collection_timestamp', ''))
        })
        
        return {
            'text': text,
            'metadata': enhanced_metadata,
            'sections': sections,
            'quality_indicators': quality_indicators,
            'startup_name': startup_name
        }
    
    def _identify_pitch_deck_sections(self, text: str) -> Dict[str, str]:
        """Identify common pitch deck sections in the text."""
        sections = {}
        
        # Common pitch deck section patterns
        section_patterns = {
            'problem': r'(?i)(problem|challenge|market need)',
            'solution': r'(?i)(solution|product|service)',
            'market_size': r'(?i)(market size|market opportunity|addressable market)',
            'business_model': r'(?i)(business model|revenue|monetization)',
            'competitive_advantage': r'(?i)(competitive advantage|moat|differentiation)',
            'team': r'(?i)(team|founders|management)',
            'financials': r'(?i)(financials|funding|investment|use of funds)',
            'traction': r'(?i)(traction|milestones|growth)',
            'roadmap': r'(?i)(roadmap|future plans|vision)'
        }
        
        text_lower = text.lower()
        
        for section_name, pattern in section_patterns.items():
            # Find sections by pattern matching
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                start_pos = match.start()
                # Find the next section or end of relevant text block
                next_section_pos = len(text)
                
                for other_pattern in section_patterns.values():
                    other_matches = list(re.finditer(other_pattern, text_lower[start_pos + 1:]))
                    if other_matches:
                        pos = other_matches[0].start() + start_pos + 1
                        next_section_pos = min(next_section_pos, pos)
                
                # Extract section content
                section_text = text[start_pos:next_section_pos].strip()
                if len(section_text) > 50:  # Minimum section length
                    sections[section_name] = section_text
                    break
        
        return sections
    
    def _assess_pitch_deck_quality(self, text: str, metadata: Dict[str, Any], sections: Dict[str, str]) -> Dict[str, float]:
        """Assess quality of pitch deck based on various indicators."""
        quality = {}
        
        # Text quality metrics
        word_count = len(text.split())
        quality['text_length'] = min(word_count / 1000, 1.0)  # Normalize to 0-1
        
        # Metadata completeness
        metadata_fields = ['title', 'author', 'creation_date']
        present_fields = sum(1 for field in metadata_fields if metadata.get(field))
        quality['metadata_completeness'] = present_fields / len(metadata_fields)
        
        # Section coverage
        expected_sections = ['problem', 'solution', 'market_size', 'team', 'financials']
        present_sections = sum(1 for section in expected_sections if section in sections)
        quality['section_coverage'] = present_sections / len(expected_sections)
        
        # Text structure (presence of headers, bullet points, etc.)
        header_count = len(re.findall(r'^#+\s', text, re.MULTILINE))
        bullet_count = len(re.findall(r'[•\-\*]\s', text))
        structure_score = min((header_count + bullet_count) / 20, 1.0)
        quality['structure_quality'] = structure_score
        
        return quality
    
    def _calculate_startup_relevance(self, text: str, startup_name: str) -> float:
        """Calculate how relevant the pitch deck is to the startup."""
        if not startup_name:
            return 0.5
        
        # Count mentions of startup name
        name_mentions = len(re.findall(re.escape(startup_name), text, re.IGNORECASE))
        
        # Business-related keywords
        business_keywords = [
            'startup', 'company', 'business', 'market', 'revenue', 'customers',
            'product', 'service', 'technology', 'innovation', 'growth', 'funding'
        ]
        
        keyword_matches = sum(1 for keyword in business_keywords 
                            if keyword.lower() in text.lower())
        
        # Calculate relevance score
        name_score = min(name_mentions / 5, 1.0)  # Cap at 5 mentions
        keyword_score = min(keyword_matches / len(business_keywords), 1.0)
        
        relevance = (name_score * 0.6 + keyword_score * 0.4)
        return min(relevance, 1.0)
    
    async def _search_for_pitch_decks(self, startup_name: str, keywords: List[str], max_results: int) -> List[str]:
        """
        Search for potential pitch deck URLs.
        
        Args:
            startup_name: Name of the startup
            keywords: Search keywords
            max_results: Maximum number of URLs to return
            
        Returns:
            List of potential pitch deck URLs
        """
        # This is a simplified implementation
        # In a real implementation, this would search through:
        # - Startup's official website
        # - AngelList/Crunchbase profiles
        # - Common pitch deck hosting sites
        # - Email/founder profiles
        
        search_queries = [
            f"{startup_name} pitch deck filetype:pdf",
            f"{startup_name} investor presentation filetype:pdf",
            f"{startup_name} deck pdf",
        ]
        
        # For now, return empty list as this requires search engine integration
        # which would need proper API keys and implementation
        return []
    
    def _get_source_type(self) -> DataSource:
        """Get the data source type for this collector."""
        return DataSource.PITCH_DECK
    
    def get_search_suggestions(self, startup_name: str) -> List[str]:
        """Get pitch deck specific search suggestions."""
        base_suggestions = super().get_search_suggestions(startup_name)
        
        pitch_deck_suggestions = [
            f"{startup_name} pitch deck pdf",
            f"{startup_name} investor presentation",
            f"{startup_name} startup deck",
            f"{startup_name} funding presentation",
            f"site:slideshare.net {startup_name} pitch deck",
            f"filetype:pdf {startup_name} deck",
            f"{startup_name} business plan pdf"
        ]
        
        return base_suggestions + pitch_deck_suggestions