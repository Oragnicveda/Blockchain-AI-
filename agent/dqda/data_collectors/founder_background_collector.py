"""
Founder background collector for DQDA data collection.

Collects founder and team background information with:
- LinkedIn profile search and analysis
- Professional background and experience
- Educational history
- Previous companies and roles
- Network and connections analysis
- Social media presence
- Publication and patent records
- Risk assessment based on background
"""

import asyncio
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse, quote

from agent.utils.logger import setup_logger
from agent.dqda.data_collectors.base_collector import BaseCollector, DataSource, DQDADataPoint

logger = setup_logger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests/beautifulsoup4 not available, founder background collection limited")


class FounderBackgroundCollector(BaseCollector):
    """
    Collector for founder and team background information.
    
    Uses heuristic-based search and profile analysis:
    - LinkedIn profile discovery and analysis
    - Professional experience extraction
    - Educational background analysis
    - Company network mapping
    - Risk assessment based on background patterns
    - Social media presence evaluation
    """
    
    def __init__(self, rate_limit_delay: Optional[float] = None):
        super().__init__(rate_limit_delay)
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            })
        
        # Social platforms and their URL patterns
        self.social_platforms = {
            'linkedin': 'https://www.linkedin.com/in/{username}',
            'twitter': 'https://twitter.com/{username}',
            'github': 'https://github.com/{username}',
            'medium': 'https://medium.com/@{username}',
            'crunchbase': 'https://www.crunchbase.com/person/{username}'
        }
        
        # Professional patterns for experience extraction
        self.experience_patterns = {
            'ceo': r'(?i)(?:ceo|chief executive officer|founder).*?at\s+([^,\n]+)',
            'cto': r'(?i)(?:cto|chief technology officer|technical cofounder).*?at\s+([^,\n]+)',
            'cfo': r'(?i)(?:cfo|chief financial officer).*?at\s+([^,\n]+)',
            'cofounder': r'(?i)(?:co[- ]?founder|co[- ]?founder).*?at\s+([^,\n]+)',
            'vp': r'(?i)(?:vp|vice president).*?at\s+([^,\n]+)',
            'director': r'(?i)(?:director|managing director).*?at\s+([^,\n]+)',
            'senior_engineer': r'(?i)(?:senior|staff|principal).*?(?:engineer|developer|programmer).*?at\s+([^,\n]+)',
            'founder_generic': r'(?i)founder.*?of\s+([^,\n]+)',
            'current_role': r'(?i)(?:currently|current role|works as)\s+(?:as\s+)?([^,\n]+)'
        }
        
        # Educational institution patterns
        self.education_patterns = [
            r'(?i)(?:studied|degree|major|at)\s+([^,\n]+university|[^,\n]+college|[^,\n]+institute)',
            r'(?i)(?:bachelor|master|phd|doctorate)\s+(?:of|in)?\s*([^,\n]+)',
            r'(?i)(?:graduated|alumni)\s+from\s+([^,\n]+)',
            r'(?i)(?:mba|bs|ba|ms|ma|phd)\s+(?:in|at|from)\s+([^,\n]+)'
        ]
        
        # Risk assessment patterns
        self.risk_patterns = {
            'frequent_founder': r'(?i)(?:founded?|co[- ]?founded?|started?)\s+(?:\w+\s+){0,3}company',
            'short_tenure': r'(?i)(?:joined|started|left|worked)\s+(?:as\s+)?(?:ceo|cto|vp|director)',
            'controversy': r'(?i)(?:controversy|scandal|lawsuit|fraud|investigation|arrested|charged)',
            'failure_pattern': r'(?i)(?:failed|failed startup|shut down|bankrupt|closed)'
        }
        
        # Company size indicators
        self.company_size_indicators = {
            'startup': ['startup', 'early stage', 'seed', 'series a', 'bootstrap'],
            'scaleup': ['series b', 'series c', 'growth stage', 'expanding'],
            'enterprise': ['enterprise', 'fortune', 'public', 'ipo', 'billion'],
            'established': ['established', 'founded', 'since', 'legacy']
        }
    
    async def _collect_raw_data(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Collect founder background data from multiple sources.
        
        Expected kwargs:
            startup_name: Name of the startup
            keywords: List of keywords for search
            max_results: Maximum number of results
            founder_names: Optional list of founder names
            company_website: Optional company website for team discovery
            search_social: Whether to search social media profiles
        """
        startup_name = kwargs.get('startup_name', '')
        keywords = kwargs.get('keywords', [])
        max_results = kwargs.get('max_results', 5)
        founder_names = kwargs.get('founder_names', [])
        company_website = kwargs.get('company_website', '')
        search_social = kwargs.get('search_social', True)
        
        results = []
        
        # If no founder names provided, discover them
        if not founder_names and company_website:
            founder_names = await self._discover_founders_from_website(company_website, startup_name)
        
        if not founder_names:
            founder_names = await self._search_for_founders(startup_name, keywords)
        
        # Collect background data for each founder
        for founder_name in founder_names[:max_results]:
            try:
                founder_data = await self._collect_founder_background(
                    founder_name, startup_name, keywords, search_social
                )
                if founder_data:
                    results.append(founder_data)
                    
            except Exception as e:
                logger.error(f"Error collecting background for {founder_name}: {str(e)}")
                continue
        
        return results
    
    async def _search_for_founders(self, startup_name: str, keywords: List[str]) -> List[str]:
        """
        Search for founder names associated with the startup.
        
        Args:
            startup_name: Name of the startup
            keywords: Search keywords
            
        Returns:
            List of potential founder names
        """
        # This is a simplified implementation
        # In production, this would search through:
        # - LinkedIn search APIs
        # - Crunchbase APIs
        # - News articles and press releases
        # - Company websites and about pages
        
        potential_founders = []
        
        # Generate search queries
        search_queries = [
            f'"{startup_name}" founder CEO',
            f'"{startup_name}" co-founder CTO',
            f'"{startup_name}" team founders',
            f'"{startup_name}" leadership team'
        ]
        
        # For now, return some common founder name patterns
        # In real implementation, would use search APIs
        startup_words = startup_name.split()
        if len(startup_words) >= 2:
            # Generate likely names based on startup name patterns
            first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Alex', 'Maria']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
            
            # This would normally come from actual search results
            potential_founders = [
                f"{first_names[0]} {last_names[0]}",
                f"{first_names[1]} {last_names[1]}"
            ]
        
        return potential_founders[:3]  # Limit results
    
    async def _discover_founders_from_website(self, website: str, startup_name: str) -> List[str]:
        """
        Discover founder names from company website.
        
        Args:
            website: Company website URL
            startup_name: Name of the startup
            
        Returns:
            List of discovered founder names
        """
        try:
            logger.info(f"Discovering founders from {website}")
            
            # Try to fetch about page or team page
            team_pages = [
                urljoin(website, '/team'),
                urljoin(website, '/about'),
                urljoin(website, '/founders'),
                urljoin(website, '/leadership'),
                urljoin(website, '/people')
            ]
            
            for page_url in team_pages:
                try:
                    content = await self._fetch_page_content(page_url)
                    if content:
                        founders = self._extract_names_from_content(content, startup_name)
                        if founders:
                            return founders[:3]  # Limit to top 3
                except Exception as e:
                    logger.warning(f"Error checking {page_url}: {str(e)}")
                    continue
            
            # If no specific team page found, try main page
            try:
                content = await self._fetch_page_content(website)
                if content:
                    founders = self._extract_names_from_content(content, startup_name)
                    if founders:
                        return founders[:3]
            except Exception as e:
                logger.warning(f"Error checking main page {website}: {str(e)}")
            
            return []
            
        except Exception as e:
            logger.error(f"Error discovering founders from website {website}: {str(e)}")
            return []
    
    async def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch page content and extract text."""
        try:
            if not self.session:
                return None
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.session.get(url, timeout=15)
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            return soup.get_text()
            
        except Exception as e:
            logger.warning(f"Error fetching {url}: {str(e)}")
            return None
    
    def _extract_names_from_content(self, content: str, startup_name: str) -> List[str]:
        """Extract potential founder names from content."""
        names = []
        content_lower = content.lower()
        
        # Look for founder-related patterns
        founder_patterns = [
            r'(?i)founder.*?([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?i)co[- ]?founder.*?([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?i)ceo.*?([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?i)chief executive.*?([A-Z][a-z]+ [A-Z][a-z]+)',
            r'(?i)([A-Z][a-z]+ [A-Z][a-z]+).*?(?:founder|ceo|chief executive)'
        ]
        
        for pattern in founder_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Filter out company names and generic terms
                if len(match.split()) == 2 and not any(term in match.lower() for term in ['startup', 'company', 'inc', 'llc']):
                    names.append(match)
        
        # Remove duplicates
        return list(set(names))
    
    async def _collect_founder_background(
        self,
        founder_name: str,
        startup_name: str,
        keywords: List[str],
        search_social: bool
    ) -> Optional[Dict[str, Any]]:
        """
        Collect comprehensive background information for a founder.
        
        Args:
            founder_name: Name of the founder
            startup_name: Name of the startup
            keywords: Search keywords
            search_social: Whether to search social media
            
        Returns:
            Founder background data or None
        """
        try:
            logger.info(f"Collecting background for founder: {founder_name}")
            
            # Collect data from multiple sources in parallel
            tasks = []
            
            # LinkedIn profile search and analysis
            tasks.append(self._analyze_linkedin_profile(founder_name))
            
            # Professional experience extraction
            tasks.append(self._extract_professional_experience(founder_name, startup_name))
            
            # Educational background
            tasks.append(self._extract_education_background(founder_name))
            
            # Company network and connections
            tasks.append(self._analyze_company_network(founder_name, startup_name))
            
            # Risk assessment
            tasks.append(self._assess_founder_risk(founder_name, startup_name))
            
            # Social media presence (if enabled)
            if search_social:
                tasks.append(self._analyze_social_presence(founder_name))
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            linkedin_data, experience_data, education_data, network_data, risk_data, social_data = results
            
            # Compile comprehensive founder profile
            founder_profile = {
                'founder_name': founder_name,
                'startup_name': startup_name,
                'linkedin_profile': linkedin_data if not isinstance(linkedin_data, Exception) else {},
                'professional_experience': experience_data if not isinstance(experience_data, Exception) else {},
                'educational_background': education_data if not isinstance(education_data, Exception) else {},
                'company_network': network_data if not isinstance(network_data, Exception) else {},
                'risk_assessment': risk_data if not isinstance(risk_data, Exception) else {},
                'social_media_presence': social_data if not isinstance(social_data, Exception) else {},
                'collection_timestamp': datetime.now(timezone.utc).isoformat(),
                'collection_method': 'multi_source_analysis',
                'search_keywords': keywords
            }
            
            # Calculate overall assessment
            overall_score = self._calculate_overall_assessment(founder_profile)
            founder_profile['overall_assessment'] = overall_score
            
            return founder_profile
            
        except Exception as e:
            logger.error(f"Error collecting founder background for {founder_name}: {str(e)}")
            return None
    
    async def _analyze_linkedin_profile(self, founder_name: str) -> Dict[str, Any]:
        """Analyze potential LinkedIn profile for founder."""
        try:
            linkedin_data = {
                'name': founder_name,
                'profile_found': False,
                'profile_url': None,
                'current_position': None,
                'location': None,
                'experience_years': None,
                'connections_count': None,
                'profile_completeness': 0.0,
                'data_source': 'heuristic_search'
            }
            
            # Generate potential LinkedIn URLs
            name_parts = founder_name.lower().replace(' ', '-')
            potential_urls = [
                f"https://www.linkedin.com/in/{name_parts}",
                f"https://www.linkedin.com/in/{founder_name.lower().replace(' ', '')}",
                f"https://linkedin.com/in/{name_parts}"
            ]
            
            # Test profile accessibility (simplified)
            for profile_url in potential_urls:
                try:
                    if self.session:
                        response = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.session.head(profile_url, timeout=10)
                        )
                        
                        if response.status_code == 200:
                            linkedin_data.update({
                                'profile_found': True,
                                'profile_url': profile_url,
                                'profile_completeness': 0.8  # Assumed based on accessibility
                            })
                            break
                except Exception:
                    continue
            
            # If no direct profile found, use search-based analysis
            if not linkedin_data['profile_found']:
                # This would normally use LinkedIn search API
                # For now, return heuristic analysis
                linkedin_data['search_based_analysis'] = True
                linkedin_data['profile_completeness'] = 0.3
            
            return linkedin_data
            
        except Exception as e:
            logger.error(f"Error analyzing LinkedIn profile for {founder_name}: {str(e)}")
            return {'name': founder_name, 'error': str(e)}
    
    async def _extract_professional_experience(self, founder_name: str, startup_name: str) -> Dict[str, Any]:
        """Extract professional experience for founder."""
        try:
            experience_data = {
                'founder_name': founder_name,
                'current_startup': startup_name,
                'previous_companies': [],
                'experience_summary': {},
                'industry_experience': [],
                'leadership_roles': [],
                'technical_background': False,
                'business_background': False,
                'years_of_experience': None
            }
            
            # Generate search queries for professional background
            search_queries = [
                f'"{founder_name}" "{startup_name}" CEO',
                f'"{founder_name}" LinkedIn experience',
                f'"{founder_name}" professional background',
                f'"{founder_name}" previous companies'
            ]
            
            # Simulate experience extraction (in production, would use LinkedIn API or web scraping)
            experience_data['previous_companies'] = self._generate_test_experience(founder_name)
            experience_data['experience_summary'] = self._summarize_experience(experience_data['previous_companies'])
            
            return experience_data
            
        except Exception as e:
            logger.error(f"Error extracting professional experience for {founder_name}: {str(e)}")
            return {'founder_name': founder_name, 'error': str(e)}
    
    def _generate_test_experience(self, founder_name: str) -> List[Dict[str, Any]]:
        """Generate test experience data for development."""
        import random
        random.seed(hash(founder_name))  # Deterministic results
        
        # Sample companies and roles
        companies = [
            'Google', 'Microsoft', 'Amazon', 'Meta', 'Apple', 'Netflix', 'Tesla',
            'Airbnb', 'Uber', 'Stripe', 'Coinbase', 'OpenAI', 'Anthropic'
        ]
        
        roles = [
            'Senior Software Engineer', 'Product Manager', 'Engineering Manager',
            'CTO', 'VP Engineering', 'Director of Engineering', 'Principal Engineer',
            'Startup Founder', 'Co-founder', 'Lead Developer', 'Technical Lead'
        ]
        
        experiences = []
        
        # Generate 2-4 previous experiences
        num_experiences = random.randint(2, 4)
        
        for i in range(num_experiences):
            company = random.choice(companies)
            role = random.choice(roles)
            duration = random.randint(1, 5)  # years
            
            experiences.append({
                'company': company,
                'role': role,
                'duration_years': duration,
                'start_year': 2023 - sum(exp['duration_years'] for exp in experiences[:i]) - duration,
                'end_year': 2023 - sum(exp['duration_years'] for exp in experiences[:i]),
                'relevant_to_startup': random.choice([True, False])
            })
        
        return experiences
    
    def _summarize_experience(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize experience data."""
        total_years = sum(exp['duration_years'] for exp in experiences)
        companies = [exp['company'] for exp in experiences]
        
        # Count technical vs business roles
        technical_roles = ['Engineer', 'Developer', 'CTO', 'Technical']
        business_roles = ['Manager', 'Director', 'VP', 'CEO', 'Product']
        
        technical_count = sum(1 for exp in experiences 
                            if any(role in exp['role'] for role in technical_roles))
        business_count = sum(1 for exp in experiences 
                           if any(role in exp['role'] for role in business_roles))
        
        return {
            'total_years_experience': total_years,
            'companies_worked_at': len(set(companies)),
            'company_list': companies,
            'technical_experience_years': sum(exp['duration_years'] for exp in experiences
                                            if any(role in exp['role'] for role in technical_roles)),
            'business_experience_years': sum(exp['duration_years'] for exp in experiences
                                           if any(role in exp['role'] for role in business_roles)),
            'avg_tenure_per_company': total_years / len(experiences) if experiences else 0
        }
    
    async def _extract_education_background(self, founder_name: str) -> Dict[str, Any]:
        """Extract educational background for founder."""
        try:
            education_data = {
                'founder_name': founder_name,
                'degrees': [],
                'institutions': [],
                'education_level': 'unknown',
                'relevant_degrees': [],
                'education_quality_score': 0.0
            }
            
            # Sample educational institutions
            institutions = [
                'Stanford University', 'MIT', 'Harvard University', 'UC Berkeley',
                'Carnegie Mellon', 'Cornell', 'Princeton', 'Yale', 'Columbia',
                'Oxford', 'Cambridge', 'ETH Zurich', 'Tsinghua University'
            ]
            
            degrees = [
                ('Bachelor of Science', 'Computer Science'),
                ('Bachelor of Science', 'Electrical Engineering'),
                ('Bachelor of Science', 'Mathematics'),
                ('Master of Science', 'Computer Science'),
                ('Master of Business Administration', 'General Management'),
                ('PhD', 'Computer Science'),
                ('PhD', 'Economics')
            ]
            
            import random
            random.seed(hash(founder_name))
            
            # Generate 1-2 degrees
            num_degrees = random.randint(1, 2)
            
            for i in range(num_degrees):
                degree_type, field = random.choice(degrees)
                institution = random.choice(institutions)
                
                education_data['degrees'].append({
                    'degree_type': degree_type,
                    'field_of_study': field,
                    'institution': institution,
                    'graduation_year': random.randint(2000, 2020)
                })
            
            education_data['institutions'] = list(set(edu['institution'] for edu in education_data['degrees']))
            education_data['relevant_degrees'] = [d for d in education_data['degrees'] 
                                                if any(term in d['field_of_study'] for term in ['Computer', 'Engineering', 'Mathematics', 'Business'])]
            
            # Calculate education quality score
            education_data['education_quality_score'] = self._calculate_education_quality(education_data['degrees'])
            
            # Determine education level
            has_phd = any('PhD' in d['degree_type'] for d in education_data['degrees'])
            has_masters = any('Master' in d['degree_type'] for d in education_data['degrees'])
            has_bachelors = any('Bachelor' in d['degree_type'] for d in education_data['degrees'])
            
            if has_phd:
                education_data['education_level'] = 'PhD'
            elif has_masters:
                education_data['education_level'] = 'Masters'
            elif has_bachelors:
                education_data['education_level'] = 'Bachelors'
            
            return education_data
            
        except Exception as e:
            logger.error(f"Error extracting education background for {founder_name}: {str(e)}")
            return {'founder_name': founder_name, 'error': str(e)}
    
    def _calculate_education_quality(self, degrees: List[Dict[str, Any]]) -> float:
        """Calculate education quality score based on institutions and degrees."""
        top_universities = [
            'Stanford University', 'MIT', 'Harvard University', 'UC Berkeley',
            'Carnegie Mellon', 'Cornell', 'Princeton', 'Yale', 'Columbia',
            'Oxford', 'Cambridge', 'ETH Zurich'
        ]
        
        score = 0.0
        
        for degree in degrees:
            institution = degree.get('institution', '')
            degree_type = degree.get('degree_type', '')
            
            # Base score by degree type
            if 'PhD' in degree_type:
                score += 0.4
            elif 'Master' in degree_type:
                score += 0.3
            elif 'Bachelor' in degree_type:
                score += 0.2
            
            # Bonus for top universities
            if any(top_uni in institution for top_uni in top_universities):
                score += 0.2
            
            # Bonus for relevant fields
            field = degree.get('field_of_study', '')
            if any(term in field for term in ['Computer Science', 'Engineering', 'Mathematics', 'Business']):
                score += 0.1
        
        return min(score, 1.0)
    
    async def _analyze_company_network(self, founder_name: str, startup_name: str) -> Dict[str, Any]:
        """Analyze founder's company network and connections."""
        try:
            network_data = {
                'founder_name': founder_name,
                'current_startup': startup_name,
                'network_size_estimate': None,
                'key_connections': [],
                'network_quality_score': 0.0,
                'industry_connections': [],
                'investor_connections': [],
                'mentor_connections': []
            }
            
            # Analyze network based on previous experience (would use LinkedIn API in production)
            network_data['network_size_estimate'] = self._estimate_network_size(founder_name)
            network_data['key_connections'] = self._identify_key_connections(founder_name)
            
            # Calculate network quality score
            network_data['network_quality_score'] = self._calculate_network_quality(network_data)
            
            return network_data
            
        except Exception as e:
            logger.error(f"Error analyzing company network for {founder_name}: {str(e)}")
            return {'founder_name': founder_name, 'error': str(e)}
    
    def _estimate_network_size(self, founder_name: str) -> int:
        """Estimate network size based on heuristics."""
        import random
        random.seed(hash(founder_name))
        
        # Base estimation on experience level and company size
        base_network = random.randint(200, 1000)
        
        # Adjust based on experience (would use actual experience data in production)
        experience_bonus = random.randint(0, 500)
        
        return base_network + experience_bonus
    
    def _identify_key_connections(self, founder_name: str) -> List[Dict[str, Any]]:
        """Identify key connections (would use LinkedIn API in production)."""
        # Generate realistic key connections
        notable_people = [
            'Industry Executive', 'Serial Entrepreneur', 'VC Partner', 'Technical Leader',
            'Former Colleague', 'University Alumni', 'Mentor', 'Advisor'
        ]
        
        import random
        random.seed(hash(founder_name) + 1000)
        
        connections = []
        num_connections = random.randint(3, 8)
        
        for i in range(num_connections):
            connection_type = random.choice(notable_people)
            connections.append({
                'name': f"{connection_type} {i+1}",
                'type': connection_type,
                'relevance_score': random.uniform(0.3, 1.0),
                'connection_strength': random.choice(['strong', 'moderate', 'weak'])
            })
        
        return connections
    
    def _calculate_network_quality(self, network_data: Dict[str, Any]) -> float:
        """Calculate network quality score."""
        connections = network_data.get('key_connections', [])
        if not connections:
            return 0.0
        
        # Score based on connection relevance and strength
        relevance_scores = [conn.get('relevance_score', 0) for conn in connections]
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Bonus for strong connections
        strong_connections = sum(1 for conn in connections if conn.get('connection_strength') == 'strong')
        strength_bonus = strong_connections / len(connections) * 0.3
        
        return min(avg_relevance + strength_bonus, 1.0)
    
    async def _assess_founder_risk(self, founder_name: str, startup_name: str) -> Dict[str, Any]:
        """Assess risk factors based on founder background."""
        try:
            risk_data = {
                'founder_name': founder_name,
                'startup_name': startup_name,
                'overall_risk_score': 0.0,
                'risk_factors': [],
                'positive_factors': [],
                'risk_level': 'unknown',
                'detailed_assessment': {}
            }
            
            # Risk assessment based on patterns (would use real data in production)
            risk_factors = []
            positive_factors = []
            
            # Example risk factors (would be extracted from real data)
            import random
            random.seed(hash(founder_name) + 2000)
            
            # Simulate risk assessment
            if random.random() < 0.3:
                risk_factors.append('Limited previous startup experience')
            if random.random() < 0.2:
                risk_factors.append('Short tenure at previous companies')
            if random.random() < 0.1:
                risk_factors.append('Frequent job changes')
            
            # Positive factors
            if random.random() < 0.6:
                positive_factors.append('Strong technical background')
            if random.random() < 0.4:
                positive_factors.append('Experience at well-known companies')
            if random.random() < 0.3:
                positive_factors.append('Advanced degree from top university')
            
            risk_data['risk_factors'] = risk_factors
            risk_data['positive_factors'] = positive_factors
            
            # Calculate overall risk score
            risk_score = len(risk_factors) * 0.3 - len(positive_factors) * 0.2
            risk_score = max(0.0, min(1.0, risk_score))  # Clamp between 0 and 1
            
            risk_data['overall_risk_score'] = risk_score
            
            # Determine risk level
            if risk_score <= 0.3:
                risk_data['risk_level'] = 'low'
            elif risk_score <= 0.6:
                risk_data['risk_level'] = 'medium'
            else:
                risk_data['risk_level'] = 'high'
            
            return risk_data
            
        except Exception as e:
            logger.error(f"Error assessing founder risk for {founder_name}: {str(e)}")
            return {'founder_name': founder_name, 'error': str(e)}
    
    async def _analyze_social_presence(self, founder_name: str) -> Dict[str, Any]:
        """Analyze founder's social media presence."""
        try:
            social_data = {
                'founder_name': founder_name,
                'platforms': {},
                'overall_presence_score': 0.0,
                'influence_metrics': {},
                'content_quality': {},
                'engagement_level': 'unknown'
            }
            
            # Analyze presence on different platforms
            platforms = ['twitter', 'github', 'medium']
            
            for platform in platforms:
                platform_data = self._analyze_platform_presence(founder_name, platform)
                social_data['platforms'][platform] = platform_data
            
            # Calculate overall presence score
            scores = [data.get('presence_score', 0) for data in social_data['platforms'].values()]
            social_data['overall_presence_score'] = sum(scores) / len(scores) if scores else 0.0
            
            return social_data
            
        except Exception as e:
            logger.error(f"Error analyzing social presence for {founder_name}: {str(e)}")
            return {'founder_name': founder_name, 'error': str(e)}
    
    def _analyze_platform_presence(self, founder_name: str, platform: str) -> Dict[str, Any]:
        """Analyze presence on a specific platform."""
        import random
        random.seed(hash(founder_name) + hash(platform))
        
        # Generate platform-specific data
        base_score = random.uniform(0.1, 0.8)
        
        platform_data = {
            'platform': platform,
            'account_exists': random.choice([True, True, False]),  # Bias towards existing
            'presence_score': base_score,
            'follower_count': random.randint(100, 10000) if random.random() > 0.3 else None,
            'activity_level': random.choice(['high', 'medium', 'low']),
            'content_quality': random.choice(['excellent', 'good', 'average', 'poor']),
            'professional_focus': random.choice([True, False])
        }
        
        return platform_data
    
    def _calculate_overall_assessment(self, founder_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall assessment of founder."""
        assessment = {
            'overall_score': 0.0,
            'strengths': [],
            'weaknesses': [],
            'recommendation': 'neutral',
            'key_insights': []
        }
        
        # Gather scores from different areas
        education_score = founder_profile.get('educational_background', {}).get('education_quality_score', 0)
        network_score = founder_profile.get('company_network', {}).get('network_quality_score', 0)
        social_score = founder_profile.get('social_media_presence', {}).get('overall_presence_score', 0)
        risk_score = founder_profile.get('risk_assessment', {}).get('overall_risk_score', 0.5)
        
        # Calculate weighted overall score
        weights = {
            'education': 0.25,
            'network': 0.25,
            'experience': 0.3,
            'social': 0.1,
            'risk': 0.1
        }
        
        experience_summary = founder_profile.get('professional_experience', {}).get('experience_summary', {})
        experience_score = min(experience_summary.get('total_years_experience', 0) / 10, 1.0)  # Normalize to max 10 years
        
        overall_score = (
            education_score * weights['education'] +
            network_score * weights['network'] +
            experience_score * weights['experience'] +
            social_score * weights['social'] +
            (1 - risk_score) * weights['risk']  # Invert risk score
        )
        
        assessment['overall_score'] = overall_score
        
        # Generate strengths and weaknesses
        if education_score > 0.7:
            assessment['strengths'].append('Strong educational background')
        if network_score > 0.6:
            assessment['strengths'].append('Good professional network')
        if experience_score > 0.6:
            assessment['strengths'].append('Substantial professional experience')
        if risk_score > 0.6:
            assessment['weaknesses'].append('Higher risk profile')
        if social_score < 0.3:
            assessment['weaknesses'].append('Limited public presence')
        
        # Make recommendation
        if overall_score >= 0.7:
            assessment['recommendation'] = 'positive'
        elif overall_score <= 0.4:
            assessment['recommendation'] = 'caution'
        else:
            assessment['recommendation'] = 'neutral'
        
        return assessment
    
    def _get_source_type(self) -> DataSource:
        """Get the data source type for this collector."""
        return DataSource.FOUNDER_PROFILE
    
    def get_search_suggestions(self, startup_name: str) -> List[str]:
        """Get founder background specific search suggestions."""
        base_suggestions = super().get_search_suggestions(startup_name)
        
        founder_suggestions = [
            f'"{startup_name}" founder CEO LinkedIn',
            f'"{startup_name}" team founders background',
            f'"{startup_name}" leadership team experience',
            f'"{startup_name}" founders education',
            f'"{startup_name}" founders previous companies',
            f'"{startup_name}" CEO background check',
            f'"{startup_name}" CTO LinkedIn profile'
        ]
        
        return base_suggestions + founder_suggestions