"""
Website crawler for DQDA data collection.

Focused website scraping with:
- Robots.txt compliance checking
- URL blacklisting support
- Rate limiting and respectful crawling
- Selective content extraction (company info, team, product)
- Error handling and graceful degradation
- Async-friendly interface for parallel crawling
"""

import asyncio
import re
import time
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urljoin, urlparse
from urllib import robotparser
from collections import deque
import hashlib

from agent.utils.logger import setup_logger
from agent.dqda.data_collectors.base_collector import BaseCollector, DataSource, DQDADataPoint

logger = setup_logger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
    BS4_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    BS4_AVAILABLE = False
    logger.warning("requests/beautifulsoup4 not available, website crawling disabled")


class WebsiteCrawler(BaseCollector):
    """
    Website crawler with focused scraping and respectful crawling practices.
    
    Features:
    - Robots.txt compliance checking
    - URL blacklisting and filtering
    - Rate limiting with configurable delays
    - Selective content extraction for startup analysis
    - Company information extraction (about, team, product)
    - Parallel crawling support
    - Error handling and graceful degradation
    """
    
    def __init__(self, rate_limit_delay: Optional[float] = None):
        super().__init__(rate_limit_delay)
        
        if REQUESTS_AVAILABLE and BS4_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
        
        # URL patterns to prioritize for startup information
        self.priority_paths = {
            'about': ['/about', '/about-us', '/company', '/team', '/founder', '/founders'],
            'product': ['/product', '/products', '/solution', '/solutions', '/services', '/platform'],
            'contact': ['/contact', '/contact-us', '/hello', '/info'],
            'legal': ['/privacy', '/terms', '/legal', '/disclaimer'],
            'blog': ['/blog', '/news', '/updates', '/posts']
        }
        
        # URL patterns to avoid (admin, internal, etc.)
        self.blocked_patterns = [
            r'/admin', r'/login', r'/signup', r'/register', r'/dashboard',
            r'/api/', r'/v1/', r'/v2/', r'/internal', r'/private',
            r'\.(jpg|jpeg|png|gif|css|js|xml|json|rss|atom)$',
            r'/wp-admin', r'/wp-content', r'/wp-includes', r'/phpmyadmin',
            r'/cgi-bin', r'/search\?', r'\?.*utm_', r'\?.*ref='
        ]
        
        # Company information extraction patterns
        self.company_info_patterns = {
            'founded_year': r'(?i)(?:founded|established|since)\s+(\d{4})',
            'employees': r'(?i)(\d+[,\d]*)\s+(?:employees|people|team members)',
            'funding': r'(?i)(?:raised|funding|investment|series [a-z])\s+[\$£€]?(\d+(?:\.\d+)?[mkb]?)',
            'valuation': r'(?i)(?:valued|valuation)\s+at\s+[\$£€]?(\d+(?:\.\d+)?[mkb]?)',
            'location': r'(?i)(?:based|headquartered|located)\s+(?:in|at)\s+([^.,\n]+)',
            'industry': r'(?i)(?:industry|sector|domain|field)\s+(?:is|of)\s+([^.,\n]+)'
        }
        
        # Team member patterns
        self.team_patterns = {
            'ceo': r'(?i)(?:ceo|chief executive|co-founder).*?([A-Z][a-z]+ [A-Z][a-z]+)',
            'cto': r'(?i)(?:cto|chief technology|co-founder).*?([A-Z][a-z]+ [A-Z][a-z]+)',
            'founder': r'(?i)(?:founder|co-founder).*?([A-Z][a-z]+ [A-Z][a-z]+)',
            'executive': r'(?i)(?:executive|vp|director|manager).*?([A-Z][a-z]+ [A-Z][a-z]+)'
        }
    
    async def _collect_raw_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect website data from startup's online presence.
        
        Expected kwargs:
            startup_name: Name of the startup
            keywords: List of keywords for search
            max_results: Maximum number of results
            base_urls: Optional list of base URLs to crawl
            crawl_depth: Maximum crawl depth (default: 2)
            max_pages: Maximum pages to crawl per domain (default: 10)
        """
        startup_name = kwargs.get('startup_name', '')
        keywords = kwargs.get('keywords', [])
        max_results = kwargs.get('max_results', 10)
        base_urls = kwargs.get('base_urls', [])
        crawl_depth = kwargs.get('crawl_depth', 2)
        max_pages = kwargs.get('max_pages', 10)
        
        results = []
        
        # If no URLs provided, search for them
        if not base_urls:
            base_urls = await self._search_for_startup_urls(startup_name, keywords)
        
        if not base_urls:
            logger.warning(f"No URLs found for startup: {startup_name}")
            return []
        
        # Crawl discovered URLs
        for base_url in base_urls[:max_results]:
            try:
                # Check robots.txt compliance
                if not await self._can_crawl(base_url):
                    logger.info(f"Skipping {base_url} due to robots.txt restrictions")
                    continue
                
                # Perform focused crawling
                crawl_result = await self._crawl_website(base_url, startup_name, keywords, crawl_depth, max_pages)
                if crawl_result:
                    results.append(crawl_result)
                    
                # Rate limiting between domains
                await asyncio.sleep(self.rate_limit_delay * 2)
                
            except Exception as e:
                logger.error(f"Error crawling {base_url}: {str(e)}")
                continue
        
        return results
    
    async def _search_for_startup_urls(self, startup_name: str, keywords: List[str]) -> List[str]:
        """
        Search for official website URLs for the startup.
        
        Args:
            startup_name: Name of the startup
            keywords: Search keywords
            
        Returns:
            List of potential website URLs
        """
        # This is a simplified implementation
        # In production, this would integrate with search APIs
        potential_urls = []
        
        # Generate likely URLs based on startup name
        base_candidates = [
            f"https://{startup_name.lower().replace(' ', '')}.com",
            f"https://www.{startup_name.lower().replace(' ', '')}.com",
            f"https://{startup_name.lower().replace(' ', ' ')}.io",
            f"https://www.{startup_name.lower().replace(' ', ' ')}.io",
            f"https://{startup_name.lower().replace(' ', '-')}.com",
            f"https://www.{startup_name.lower().replace(' ', '-')}.com"
        ]
        
        # Test which URLs are valid (basic connectivity check)
        for url in base_candidates:
            if await self._is_valid_url(url):
                potential_urls.append(url)
        
        return potential_urls[:3]  # Return top 3 candidates
    
    async def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible."""
        if not self.session:
            return False
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.session.head(url, timeout=10)
            )
            return response.status_code < 400
            
        except Exception:
            return False
    
    async def _can_crawl(self, url: str) -> bool:
        """
        Check if URL can be crawled according to robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if crawling is allowed
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Fetch robots.txt
            robots_url = urljoin(base_url, '/robots.txt')
            
            if not self.session:
                return True  # Allow if we can't check
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.session.get(robots_url, timeout=10)
            )
            
            if response.status_code == 404:
                return True  # No robots.txt, allow crawling
            
            if response.status_code >= 400:
                return True  # Error fetching robots, allow crawling
            
            # Parse robots.txt
            robots_parser = robotparser.RobotFileParser()
            try:
                robots_parser.set_url(f"{base_url}/robots.txt")
                robots_parser.read()
                
                # Check if user agent is allowed
                user_agent = self.session.headers.get('User-Agent', '*') if self.session else '*'
                if not robots_parser.can_fetch(user_agent, '/'):
                    return False
            except Exception:
                # If parsing fails, allow crawling
                pass
            
            return True
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {str(e)}")
            return True  # Allow on error
    
    async def _crawl_website(
        self,
        base_url: str,
        startup_name: str,
        keywords: List[str],
        max_depth: int,
        max_pages: int
    ) -> Optional[Dict[str, Any]]:
        """
        Perform focused crawling of a website.
        
        Args:
            base_url: Base URL to start crawling from
            startup_name: Name of the startup
            keywords: Search keywords
            max_depth: Maximum crawl depth
            max_pages: Maximum pages to crawl
            
        Returns:
            Crawl results or None if crawling fails
        """
        try:
            logger.info(f"Starting crawl of {base_url} (depth: {max_depth}, max pages: {max_pages})")
            
            # Initialize crawl state
            visited_urls = set()
            url_queue = deque([(base_url, 0)])  # (url, depth)
            crawled_pages = []
            company_data = {}
            site_structure = {}
            
            while url_queue and len(crawled_pages) < max_pages:
                current_url, depth = url_queue.popleft()
                
                if current_url in visited_urls or depth > max_depth:
                    continue
                
                # Check if URL should be blocked
                if self._should_block_url(current_url):
                    continue
                
                visited_urls.add(current_url)
                
                try:
                    # Fetch and parse page
                    page_data = await self._fetch_and_parse_page(current_url)
                    if page_data:
                        crawled_pages.append(page_data)
                        
                        # Extract company information
                        page_company_data = self._extract_company_info(page_data['content'], startup_name)
                        self._merge_company_data(company_data, page_company_data)
                        
                        # Update site structure
                        site_structure[urlparse(current_url).path] = {
                            'title': page_data.get('title', ''),
                            'content_length': len(page_data.get('content', '')),
                            'priority_page': self._get_page_priority(urlparse(current_url).path)
                        }
                        
                        # Add new URLs to queue (respecting depth limit)
                        if depth < max_depth:
                            new_urls = self._extract_internal_links(
                                current_url,
                                page_data.get('html', '')
                            )
                            for new_url in new_urls:
                                if new_url not in visited_urls:
                                    url_queue.append((new_url, depth + 1))
                
                except Exception as e:
                    logger.warning(f"Error crawling {current_url}: {str(e)}")
                    continue
            
            # Compile results
            crawl_result = {
                'base_url': base_url,
                'crawled_pages': crawled_pages,
                'company_information': company_data,
                'site_structure': site_structure,
                'crawl_stats': {
                    'pages_crawled': len(crawled_pages),
                    'total_urls_visited': len(visited_urls),
                    'crawl_depth': max_depth,
                    'crawl_duration': time.time() - start_time if 'start_time' in locals() else 0
                },
                'collection_method': 'website_crawling',
                'startup_name': startup_name,
                'search_keywords': keywords
            }
            
            logger.info(f"Crawl completed for {base_url}: {len(crawled_pages)} pages")
            return crawl_result
            
        except Exception as e:
            logger.error(f"Error crawling website {base_url}: {str(e)}")
            return None
    
    async def _fetch_and_parse_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a single web page.
        
        Args:
            url: URL to fetch
            
        Returns:
            Page data or None if fetching fails
        """
        try:
            if not self.session:
                return None
            
            # Fetch page
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.session.get(url, timeout=15)
            )
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content
            title = self._extract_page_title(soup)
            content = self._extract_page_content(soup)
            meta_description = self._extract_meta_description(soup)
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'meta_description': meta_description,
                'html': str(soup),
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', '')
            }
            
        except Exception as e:
            logger.warning(f"Error fetching page {url}: {str(e)}")
            return None
    
    def _extract_page_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from soup."""
        title_tag = soup.find('title')
        return title_tag.get_text().strip() if title_tag else ''
    
    def _extract_page_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page."""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try to find main content area
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            text = main_content.get_text()
        else:
            text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from page."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        return ''
    
    def _should_block_url(self, url: str) -> bool:
        """
        Check if URL should be blocked based on patterns.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL should be blocked
        """
        for pattern in self.blocked_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def _extract_internal_links(self, base_url: str, html: str) -> List[str]:
        """
        Extract internal links from HTML content.
        
        Args:
            base_url: Base URL for resolving relative URLs
            html: HTML content
            
        Returns:
            List of internal URLs
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            base_domain = urlparse(base_url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                parsed_url = urlparse(full_url)
                
                # Only include internal links
                if parsed_url.netloc == base_domain:
                    # Filter out blocked patterns
                    if not self._should_block_url(full_url):
                        links.append(full_url)
            
            # Remove duplicates and limit
            return list(set(links))[:10]  # Limit per page
            
        except Exception as e:
            logger.warning(f"Error extracting links: {str(e)}")
            return []
    
    def _extract_company_info(self, content: str, startup_name: str) -> Dict[str, Any]:
        """
        Extract company information from page content.
        
        Args:
            content: Page content
            startup_name: Name of the startup
            
        Returns:
            Extracted company information
        """
        company_info = {}
        content_lower = content.lower()
        startup_name_lower = startup_name.lower()
        
        # Extract company information using patterns
        for info_type, pattern in self.company_info_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                company_info[info_type] = matches[0]  # Take first match
        
        # Extract team information
        team_info = {}
        for role, pattern in self.team_patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                team_info[role] = matches
        
        if team_info:
            company_info['team'] = team_info
        
        # Check for startup name mentions
        if startup_name_lower in content_lower:
            company_info['startup_mentioned'] = True
            company_info['name_variations'] = self._find_name_variations(content, startup_name)
        
        # Extract key products/services mentioned
        key_terms = ['product', 'service', 'solution', 'platform', 'technology']
        for term in key_terms:
            if term in content_lower:
                if 'key_terms_mentioned' not in company_info:
                    company_info['key_terms_mentioned'] = []
                company_info['key_terms_mentioned'].append(term)
        
        return company_info
    
    def _find_name_variations(self, content: str, startup_name: str) -> List[str]:
        """Find variations of the startup name in content."""
        variations = set()
        
        # Common variations
        name_parts = startup_name.split()
        if len(name_parts) > 1:
            # Add acronym
            acronym = ''.join(part[0] for part in name_parts)
            variations.add(acronym.upper())
        
        return list(variations)
    
    def _merge_company_data(self, existing: Dict[str, Any], new: Dict[str, Any]) -> None:
        """Merge new company data with existing data."""
        for key, value in new.items():
            if key in existing:
                if isinstance(value, list) and isinstance(existing[key], list):
                    existing[key].extend(value)
                elif isinstance(value, str) and existing[key]:
                    # Keep first non-empty value
                    if not existing[key]:
                        existing[key] = value
            else:
                existing[key] = value
    
    def _get_page_priority(self, path: str) -> str:
        """Get priority level of a page based on its path."""
        path_lower = path.lower()
        
        for priority, paths in self.priority_paths.items():
            if any(path_l in path_lower for path_l in paths):
                return priority
        
        return 'general'
    
    def _get_source_type(self) -> DataSource:
        """Get the data source type for this collector."""
        return DataSource.WEBSITE
    
    def get_search_suggestions(self, startup_name: str) -> List[str]:
        """Get website specific search suggestions."""
        base_suggestions = super().get_search_suggestions(startup_name)
        
        website_suggestions = [
            f"site:{startup_name.lower().replace(' ', '')}.com",
            f"site:{startup_name.lower().replace(' ', ' ')}.io",
            f'"{startup_name}" about company',
            f'"{startup_name}" team founders',
            f'"{startup_name}" contact information',
            f'"{startup_name}" official website'
        ]
        
        return base_suggestions + website_suggestions
    
    def add_blocked_patterns(self, patterns: List[str]) -> None:
        """
        Add additional URL patterns to block.
        
        Args:
            patterns: List of regex patterns to block
        """
        self.blocked_patterns.extend(patterns)
    
    def set_priority_paths(self, priority_paths: Dict[str, List[str]]) -> None:
        """
        Set custom priority paths for page categorization.
        
        Args:
            priority_paths: Dictionary of category to path patterns
        """
        self.priority_paths = priority_paths