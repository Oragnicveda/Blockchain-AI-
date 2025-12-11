"""
Whitepaper processor for DQDA data collection.

Processes whitepapers with:
- Clean text extraction from PDF/DOC formats
- Section tagging and structural analysis
- Technical content identification
- Academic/professional writing quality assessment
- Domain-specific terminology extraction
"""

import asyncio
import io
import re
import os
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

from agent.utils.logger import setup_logger
from agent.dqda.data_collectors.base_collector import BaseCollector, DataSource, DQDADataPoint

logger = setup_logger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class WhitepaperProcessor(BaseCollector):
    """
    Processor for technical whitepapers with text cleaning and section tagging.
    
    Supports:
    - Multiple document formats (PDF, HTML, TXT)
    - Automatic section identification and tagging
    - Technical terminology extraction
    - Academic writing quality assessment
    - Blockchain/crypto specific terminology detection
    """
    
    def __init__(self):
        super().__init__()
        self.session = None
        if REQUESTS_AVAILABLE:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        
        # Technical terminology patterns for different domains
        self.terminology_patterns = {
            'blockchain': [
                r'\b(consensus|mining|hash|blockchain|distributed|ledger|decentralized|cryptocurrency)\b',
                r'\b(token|crypto|wallet|private key|public key|transaction|smart contract)\b',
                r'\b(ethereum|bitcoin|defi|nft|dao|web3)\b'
            ],
            'ai_ml': [
                r'\b(machine learning|neural network|deep learning|algorithm|model|training)\b',
                r'\b(artificial intelligence|ml|ai|nlp|computer vision|classification)\b',
                r'\b(tensor|gradient|backpropagation|supervised|unsupervised|reinforcement)\b'
            ],
            'general_tech': [
                r'\b(api|database|server|cloud|microservices|api|protocol)\b',
                r'\b(scalability|performance|optimization|architecture|framework)\b',
                r'\b(startup|vc|investment|funding|market|business model)\b'
            ]
        }
    
    async def _collect_raw_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect whitepaper data from multiple sources.
        
        Expected kwargs:
            startup_name: Name of the startup
            keywords: List of keywords for search
            max_results: Maximum number of results
            whitepaper_urls: Optional list of direct whitepaper URLs
            whitepaper_path: Optional local path to whitepaper
            document_formats: Optional list of formats to accept ('pdf', 'html', 'txt')
        """
        startup_name = kwargs.get('startup_name', '')
        keywords = kwargs.get('keywords', [])
        max_results = kwargs.get('max_results', 5)
        whitepaper_urls = kwargs.get('whitepaper_urls', [])
        whitepaper_path = kwargs.get('whitepaper_path')
        document_formats = kwargs.get('document_formats', ['pdf', 'html', 'txt'])
        
        results = []
        
        # Process local file if provided
        if whitepaper_path:
            if os.path.exists(whitepaper_path):
                data = await self._process_whitepaper_file(whitepaper_path, startup_name, keywords, document_formats)
                if data:
                    results.append(data)
            else:
                logger.warning(f"Whitepaper file not found: {whitepaper_path}")

        # Process provided whitepaper URLs
        if whitepaper_urls and len(results) < max_results:
            for url in whitepaper_urls[:max_results - len(results)]:
                data = await self._process_whitepaper_url(url, startup_name, keywords, document_formats)
                if data:
                    results.append(data)
                    if len(results) >= max_results:
                        break
        
        # Search for additional whitepapers if needed
        if len(results) < max_results:
            search_urls = await self._search_for_whitepapers(startup_name, keywords, max_results - len(results))
            for url in search_urls:
                data = await self._process_whitepaper_url(url, startup_name, keywords, document_formats)
                if data:
                    results.append(data)
                    if len(results) >= max_results:
                        break
        
        return results
    
    async def _process_whitepaper_file(self, file_path: str, startup_name: str, keywords: List[str], formats: List[str]) -> Optional[Dict[str, Any]]:
        """
        Process a whitepaper from a local file.
        
        Args:
            file_path: Path to the whitepaper file
            startup_name: Name of the startup
            keywords: Search keywords
            formats: Accepted document formats
            
        Returns:
            Raw data dictionary or None if processing fails
        """
        try:
            logger.info(f"Processing whitepaper from file: {file_path}")
            
            # Determine document type
            doc_type = 'unknown'
            if file_path.lower().endswith('.pdf'):
                doc_type = 'pdf'
            elif file_path.lower().endswith('.txt'):
                doc_type = 'txt'
            elif file_path.lower().endswith('.html') or file_path.lower().endswith('.htm'):
                doc_type = 'html'
            
            if doc_type not in formats:
                logger.warning(f"Document type {doc_type} not in accepted formats: {formats}")
                return None
            
            # Read content
            try:
                with open(file_path, 'rb') as f:
                    content_bytes = f.read()
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {str(e)}")
                return None

            content = {'content': content_bytes, 'content_type': doc_type}
            
            # Extract and clean text
            processed_content = await self._extract_and_clean_text(content, doc_type)
            if not processed_content:
                return None
            
            # Analyze content structure and quality
            analysis_result = self._analyze_whitepaper_content(processed_content, startup_name)
            
            return {
                'url': f"file://{os.path.abspath(file_path)}",
                'content': analysis_result['clean_text'],
                'document_type': doc_type,
                'sections': analysis_result['sections'],
                'technical_terminology': analysis_result['terminology'],
                'writing_quality': analysis_result['quality_metrics'],
                'key_insights': analysis_result['insights'],
                'collection_method': f'local_{doc_type}_processing',
                'startup_name': startup_name,
                'search_keywords': keywords
            }
            
        except Exception as e:
            logger.error(f"Error processing whitepaper from file {file_path}: {str(e)}")
            return None

    async def _process_whitepaper_url(self, url: str, startup_name: str, keywords: List[str], formats: List[str]) -> Optional[Dict[str, Any]]:
        """
        Process a whitepaper from a URL.
        
        Args:
            url: URL of the whitepaper
            startup_name: Name of the startup
            keywords: Search keywords
            formats: Accepted document formats
            
        Returns:
            Raw data dictionary or None if processing fails
        """
        try:
            logger.info(f"Processing whitepaper from: {url}")
            
            # Download content
            content = await self._download_whitepaper(url)
            if not content:
                return None
            
            # Determine document type and process accordingly
            doc_type = self._determine_document_type(url, content)
            if doc_type not in formats:
                logger.warning(f"Document type {doc_type} not in accepted formats: {formats}")
                return None
            
            # Extract and clean text
            processed_content = await self._extract_and_clean_text(content, doc_type)
            if not processed_content:
                return None
            
            # Analyze content structure and quality
            analysis_result = self._analyze_whitepaper_content(processed_content, startup_name)
            
            return {
                'url': url,
                'content': analysis_result['clean_text'],
                'document_type': doc_type,
                'sections': analysis_result['sections'],
                'technical_terminology': analysis_result['terminology'],
                'writing_quality': analysis_result['quality_metrics'],
                'key_insights': analysis_result['insights'],
                'collection_method': f'{doc_type}_processing',
                'startup_name': startup_name,
                'search_keywords': keywords
            }
            
        except Exception as e:
            logger.error(f"Error processing whitepaper from {url}: {str(e)}")
            return None
    
    async def _download_whitepaper(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Download whitepaper content from URL.
        
        Args:
            url: URL to download from
            
        Returns:
            Dictionary with content and metadata or None
        """
        if not self.session:
            logger.warning("No session available for whitepaper download")
            return None
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.session.get(url, timeout=30)
            )
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            
            return {
                'content': response.content,
                'content_type': content_type,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error downloading whitepaper from {url}: {str(e)}")
            return None
    
    def _determine_document_type(self, url: str, content: Dict[str, Any]) -> str:
        """
        Determine the document type based on URL and content.
        
        Args:
            url: Source URL
            content: Downloaded content
            
        Returns:
            Document type ('pdf', 'html', 'txt')
        """
        url_lower = url.lower()
        content_type = content.get('content_type', '').lower()
        
        # Check URL extension first
        if url_lower.endswith('.pdf'):
            return 'pdf'
        elif url_lower.endswith('.txt'):
            return 'txt'
        elif any(url_lower.endswith(f'.{ext}') for ext in ['doc', 'docx']):
            return 'doc'
        
        # Check content type
        if 'pdf' in content_type:
            return 'pdf'
        elif 'html' in content_type:
            return 'html'
        elif 'text' in content_type:
            return 'txt'
        
        # Default to HTML for web pages
        if 'http' in url_lower:
            return 'html'
        
        return 'unknown'
    
    async def _extract_and_clean_text(self, content: Dict[str, Any], doc_type: str) -> Optional[Dict[str, str]]:
        """
        Extract and clean text from document content.
        
        Args:
            content: Document content
            doc_type: Type of document
            
        Returns:
            Dictionary with extracted and cleaned text
        """
        try:
            if doc_type == 'pdf':
                return await self._extract_pdf_text(content['content'])
            elif doc_type == 'html':
                return await self._extract_html_text(content['content'])
            elif doc_type == 'txt':
                return await self._extract_txt_text(content['content'])
            else:
                logger.warning(f"Unsupported document type: {doc_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting text from {doc_type}: {str(e)}")
            return None
    
    async def _extract_pdf_text(self, pdf_content: bytes) -> Optional[Dict[str, str]]:
        """Extract text from PDF content."""
        try:
            if not PDF_AVAILABLE:
                # Fallback: try to extract basic text from PDF bytes
                return await self._extract_pdf_fallback(pdf_content)
            
            # Use PyPDF2 for extraction
            import PyPDF2
            import io
            
            pdf_stream = io.BytesIO(pdf_content)
            
            extracted_text = await asyncio.get_event_loop().run_in_executor(
                None,
                self._pypdf2_text_extraction,
                pdf_stream
            )
            
            return {
                'raw_text': extracted_text,
                'cleaned_text': self._clean_text(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {str(e)}")
            return None
    
    def _pypdf2_text_extraction(self, pdf_stream: io.BytesIO) -> str:
        """Extract text using PyPDF2."""
        import PyPDF2
        
        text_parts = []
        with PyPDF2.PdfReader(pdf_stream) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n'.join(text_parts)
    
    async def _extract_pdf_fallback(self, pdf_content: bytes) -> Optional[Dict[str, str]]:
        """Fallback PDF extraction without specialized libraries."""
        try:
            # Very basic text extraction - look for readable ASCII
            import re
            
            # Find text-like content in PDF
            text_pattern = re.compile(rb'[A-Za-z0-9\s.,;:!?\-\'"()]{20,}')
            matches = text_pattern.findall(pdf_content)
            
            if matches:
                extracted = b' '.join(matches).decode('ascii', errors='ignore')
                return {
                    'raw_text': extracted,
                    'cleaned_text': self._clean_text(extracted)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Fallback PDF extraction failed: {str(e)}")
            return None
    
    async def _extract_html_text(self, html_content: bytes) -> Optional[Dict[str, str]]:
        """Extract and clean text from HTML content."""
        try:
            from bs4 import BeautifulSoup
            
            html_text = await asyncio.get_event_loop().run_in_executor(
                None,
                self._beautifulsoup_extraction,
                html_content
            )
            
            return {
                'raw_text': html_text,
                'cleaned_text': self._clean_text(html_text)
            }
            
        except Exception as e:
            logger.error(f"HTML text extraction failed: {str(e)}")
            return None
    
    def _beautifulsoup_extraction(self, html_content: bytes) -> str:
        """Extract text using BeautifulSoup."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines and join
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    async def _extract_txt_text(self, txt_content: bytes) -> Optional[Dict[str, str]]:
        """Extract text from plain text content."""
        try:
            text = txt_content.decode('utf-8', errors='ignore')
            return {
                'raw_text': text,
                'cleaned_text': self._clean_text(text)
            }
            
        except Exception as e:
            logger.error(f"TXT text extraction failed: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text for analysis.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-printable characters except basic punctuation
        text = re.sub(r'[^\w\s.,;:!?\-\'"()\[\]{}]', '', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    def _analyze_whitepaper_content(self, processed_content: Dict[str, str], startup_name: str) -> Dict[str, Any]:
        """
        Analyze whitepaper content for structure, quality, and insights.
        
        Args:
            processed_content: Processed document content
            startup_name: Name of the startup
            
        Returns:
            Analysis results
        """
        clean_text = processed_content['clean_text']
        
        # Identify sections
        sections = self._identify_sections(clean_text)
        
        # Extract technical terminology
        terminology = self._extract_technical_terminology(clean_text)
        
        # Assess writing quality
        quality_metrics = self._assess_writing_quality(clean_text)
        
        # Extract key insights
        insights = self._extract_key_insights(clean_text, terminology)
        
        # Calculate relevance to startup
        relevance_score = self._calculate_startup_relevance(clean_text, startup_name)
        
        return {
            'clean_text': clean_text,
            'sections': sections,
            'terminology': terminology,
            'quality_metrics': quality_metrics,
            'insights': insights,
            'relevance_score': relevance_score
        }
    
    def _identify_sections(self, text: str) -> Dict[str, str]:
        """Identify and extract sections from whitepaper text."""
        sections = {}
        
        # Common whitepaper section patterns
        section_patterns = [
            (r'(?i)^#+\s*(.+?)$', 'markdown_headers'),
            (r'(?i)^(\d+\.?\s*[^.]+?)$', 'numbered_sections'),
            (r'(?i)^([A-Z][A-Z\s]+[A-Z])$', 'all_caps_headers'),
            (r'(?i)(abstract|introduction|methodology|results|conclusion|references)',
             'keyword_based')
        ]
        
        lines = text.split('\n')
        current_section = 'introduction'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            is_header = False
            
            # Markdown headers
            if re.match(r'^#+\s+(.+?)$', line, re.IGNORECASE):
                # Save previous section
                if current_content:
                    sections[current_section] = ' '.join(current_content)
                
                # Start new section
                current_section = re.sub(r'[^a-z0-9]', '_', line.lower().strip('# '))
                current_content = []
                is_header = True
            
            # Numbered sections
            elif re.match(r'^\d+\.?\s+[^.]+$', line, re.IGNORECASE):
                # Save previous section
                if current_content:
                    sections[current_section] = ' '.join(current_content)
                
                # Start new section
                current_section = re.sub(r'[^a-z0-9]', '_', line.lower())
                current_content = []
                is_header = True
            
            # All caps headers (short lines)
            elif len(line) < 50 and line.isupper() and len(line.split()) < 8:
                # Save previous section
                if current_content:
                    sections[current_section] = ' '.join(current_content)
                
                # Start new section
                current_section = re.sub(r'[^a-z0-9]', '_', line.lower())
                current_content = []
                is_header = True
            
            if not is_header:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = ' '.join(current_content)
        
        return sections
    
    def _extract_technical_terminology(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Extract and categorize technical terminology."""
        terminology = {}
        text_lower = text.lower()
        
        for domain, patterns in self.terminology_patterns.items():
            found_terms = []
            pattern_matches = {}
            
            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                for match in matches:
                    if match not in found_terms:
                        found_terms.append(match)
                
                # Count pattern occurrences
                occurrences = len(re.findall(pattern, text_lower))
                pattern_matches[pattern] = occurrences
            
            if found_terms:
                terminology[domain] = {
                    'terms': found_terms,
                    'frequency': len(found_terms),
                    'pattern_matches': pattern_matches
                }
        
        return terminology
    
    def _assess_writing_quality(self, text: str) -> Dict[str, float]:
        """Assess the quality of academic/professional writing."""
        quality = {}
        
        # Text length and structure
        word_count = len(text.split())
        sentence_count = len(re.split(r'[.!?]+', text))
        
        quality['word_count'] = word_count
        quality['sentence_count'] = sentence_count
        quality['avg_words_per_sentence'] = word_count / max(sentence_count, 1)
        
        # Reading level (simplified Flesch reading ease approximation)
        syllables = self._count_syllables(text)
        if sentence_count > 0 and word_count > 0:
            reading_ease = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllables / word_count)
            quality['reading_ease'] = max(0, min(100, reading_ease)) / 100  # Normalize to 0-1
        
        # Structure indicators
        has_abstract = bool(re.search(r'(?i)abstract|summary', text[:500]))
        has_references = bool(re.search(r'(?i)references|bibliography|citations?', text))
        has_figures = bool(re.search(r'(?i)figure|table|diagram', text))
        
        quality['has_abstract'] = 1.0 if has_abstract else 0.0
        quality['has_references'] = 1.0 if has_references else 0.0
        quality['has_figures'] = 1.0 if has_figures else 0.0
        
        # Academic language indicators
        academic_words = [
            'analysis', 'methodology', 'framework', 'algorithm', 'implementation',
            'evaluation', 'performance', 'optimization', 'architecture', 'design'
        ]
        academic_count = sum(1 for word in academic_words if word.lower() in text.lower())
        quality['academic_language'] = min(academic_count / len(academic_words), 1.0)
        
        return quality
    
    def _count_syllables(self, text: str) -> int:
        """Approximate syllable count for readability assessment."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        syllable_count = 0
        
        for word in words:
            # Simple vowel-based syllable counting
            vowels = len(re.findall(r'[aeiouy]+', word))
            # Adjust for silent 'e'
            if word.endswith('e') and vowels > 1:
                vowels -= 1
            # Ensure at least one syllable per word
            syllable_count += max(vowels, 1)
        
        return syllable_count
    
    def _extract_key_insights(self, text: str, terminology: Dict[str, Dict[str, Any]]) -> List[str]:
        """Extract key insights and findings from the whitepaper."""
        insights = []
        
        # Look for key insight patterns
        insight_patterns = [
            r'(?i)(?:our|this) (?:\w+\s+)?(?:\w+\s+)?(?:approach|method|algorithm|solution)\s+(?:provides|delivers|achieves|enables)\s+([^.]+)',
            r'(?i)(?:results? show|we (?:find|show|demonstrate))\s+that\s+([^.]+)',
            r'(?i)(?:key finding|main contribution|significant result)\s+(?:is|:)\s+([^.]+)',
            r'(?i)(?:in conclusion|our work|this paper)\s+(?:demonstrates?|shows?|proves?|indicates?)\s+([^.]+)'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, text)
            for match in matches[:3]:  # Limit to top 3 per pattern
                insight = match.strip()
                if len(insight) > 20 and len(insight) < 200:  # Reasonable insight length
                    insights.append(insight)
        
        # Add domain-specific insights
        if 'blockchain' in terminology:
            blockchain_insights = self._extract_blockchain_insights(text)
            insights.extend(blockchain_insights)
        
        return insights[:10]  # Limit total insights
    
    def _extract_blockchain_insights(self, text: str) -> List[str]:
        """Extract blockchain-specific insights."""
        insights = []
        
        # Look for consensus mechanisms
        consensus_patterns = [
            r'(?i)(?:uses?|implements?|based on)\s+(proof of [a-z]+)',
            r'(?i)(consensus mechanism|consensus algorithm)\s+([^.]+)'
        ]
        
        for pattern in consensus_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                insights.append(f"Consensus mechanism: {match.strip()}")
        
        # Look for performance metrics
        performance_patterns = [
            r'(?i)(\d+\.?\d*)\s*(?:tps|transactions per second|throughput)',
            r'(?i)(?:scales to|can handle)\s+(\d+\.?\d*)\s*(?:transactions|users)'
        ]
        
        for pattern in performance_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                insights.append(f"Performance metric: {match}")
        
        return insights
    
    def _calculate_startup_relevance(self, text: str, startup_name: str) -> float:
        """Calculate relevance of whitepaper to the startup."""
        if not startup_name:
            return 0.5
        
        text_lower = text.lower()
        
        # Startup name mentions
        name_mentions = len(re.findall(re.escape(startup_name), text_lower))
        
        # Business-related keywords
        business_keywords = [
            'startup', 'company', 'business', 'commercial', 'enterprise',
            'market', 'customers', 'users', 'revenue', 'profit', 'scalability',
            'implementation', 'deployment', 'production'
        ]
        
        keyword_matches = sum(1 for keyword in business_keywords 
                            if keyword in text_lower)
        
        # Technical depth indicator
        technical_indicators = [
            'algorithm', 'implementation', 'optimization', 'performance',
            'architecture', 'framework', 'system', 'platform'
        ]
        
        technical_matches = sum(1 for indicator in technical_indicators 
                              if indicator in text_lower)
        
        # Calculate relevance
        name_score = min(name_mentions / 3, 1.0)  # Cap at 3 mentions
        keyword_score = min(keyword_matches / len(business_keywords), 1.0)
        technical_score = min(technical_matches / len(technical_indicators), 1.0)
        
        relevance = (name_score * 0.5 + keyword_score * 0.3 + technical_score * 0.2)
        return min(relevance, 1.0)
    
    async def _search_for_whitepapers(self, startup_name: str, keywords: List[str], max_results: int) -> List[str]:
        """
        Search for whitepaper URLs related to the startup.
        
        Args:
            startup_name: Name of the startup
            keywords: Search keywords
            max_results: Maximum number of URLs to return
            
        Returns:
            List of potential whitepaper URLs
        """
        # Simplified implementation
        # In production, this would search through:
        # - Research paper databases (arXiv, IEEE, ACM)
        # - Startup's official documentation
        # - Academic institution repositories
        # - Company blog/technical posts
        
        search_queries = [
            f"{startup_name} whitepaper filetype:pdf",
            f"{startup_name} technical paper filetype:pdf",
            f"{startup_name} research paper filetype:pdf",
        ]
        
        # Return empty list for now - would need search API integration
        return []
    
    def _get_source_type(self) -> DataSource:
        """Get the data source type for this collector."""
        return DataSource.WHITEPAPER
    
    def get_search_suggestions(self, startup_name: str) -> List[str]:
        """Get whitepaper specific search suggestions."""
        base_suggestions = super().get_search_suggestions(startup_name)
        
        whitepaper_suggestions = [
            f"{startup_name} whitepaper pdf",
            f"{startup_name} technical paper",
            f"{startup_name} research paper",
            f"{startup_name} documentation",
            f"filetype:pdf {startup_name} whitepaper",
            f"site:arxiv.org {startup_name}",
            f"site:ieee.org {startup_name} {startup_name}"
        ]
        
        return base_suggestions + whitepaper_suggestions