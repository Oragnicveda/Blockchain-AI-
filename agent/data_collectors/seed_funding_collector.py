import requests
from typing import List, Dict, Optional
from datetime import datetime
from fake_useragent import UserAgent
from retry import retry
from agent.utils.logger import setup_logger
from agent.utils.config import Config

logger = setup_logger(__name__)


class SeedFundingCollector:
    """Collector for seed funding rounds from crypto startups with investor-focused metrics"""

    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.config = Config()

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def collect_seed_funding_data(self, max_results: int = 50) -> List[Dict]:
        """
        Collect seed funding data from crypto startups with investor-focused metrics.
        Returns data with source/site names for investor tracking.
        """
        logger.info("Collecting seed funding data from crypto startups")
        
        all_seed_rounds = []
        
        # Collect from various sources
        all_seed_rounds.extend(self._get_crunchbase_seed_data(max_results))
        all_seed_rounds.extend(self._get_pitchbook_seed_data(max_results))
        all_seed_rounds.extend(self._get_techcrunch_seed_data(max_results))
        all_seed_rounds.extend(self._get_cbinsights_seed_data(max_results))
        
        logger.info(f"Collected {len(all_seed_rounds)} seed funding rounds")
        return all_seed_rounds[:max_results]

    def _get_crunchbase_seed_data(self, max_results: int) -> List[Dict]:
        """Fetch seed funding data from Crunchbase API (simulated)"""
        logger.info("Fetching seed funding data from Crunchbase")
        
        seed_data = [
            {
                'startup_name': 'Helium Foundation',
                'funding_amount': '$20M',
                'funding_round': 'Seed',
                'announcement_date': '2023-06-15',
                'investors': ['Animoca Brands', 'Dragonfly Capital', 'Khaled Vosti'],
                'num_investors': 3,
                'source_site': 'Crunchbase',
                'source_url': 'https://www.crunchbase.com/organization/helium',
                'description': 'Decentralized wireless network for IoT devices',
                'headquarters': 'San Francisco, USA',
                'industry': 'Blockchain',
                'investor_type': ['VC Firms', 'Angel Investors'],
                'average_investment_per_investor': '$6.67M',
                'lead_investor': 'Animoca Brands',
                'funding_timeline': 'Early Stage'
            },
            {
                'startup_name': 'Magic Eden',
                'funding_amount': '$27M',
                'funding_round': 'Seed Round',
                'announcement_date': '2023-05-20',
                'investors': ['Electric Capital', 'Sequoia Capital', 'Paradigm'],
                'num_investors': 3,
                'source_site': 'Crunchbase',
                'source_url': 'https://www.crunchbase.com/organization/magic-eden',
                'description': 'Multi-chain NFT marketplace',
                'headquarters': 'San Francisco, USA',
                'industry': 'NFT/Web3',
                'investor_type': ['VC Firms'],
                'average_investment_per_investor': '$9M',
                'lead_investor': 'Electric Capital',
                'funding_timeline': 'Early Stage'
            },
            {
                'startup_name': 'Sui Network (Mysten Labs)',
                'funding_amount': '$36M',
                'funding_round': 'Seed',
                'announcement_date': '2023-04-10',
                'investors': ['Andreessen Horowitz', 'Lightspeed Venture Partners', 'Tiger Global'],
                'num_investors': 3,
                'source_site': 'Crunchbase',
                'source_url': 'https://www.crunchbase.com/organization/mysten-labs',
                'description': 'Layer 1 blockchain platform',
                'headquarters': 'San Francisco, USA',
                'industry': 'Blockchain',
                'investor_type': ['VC Firms'],
                'average_investment_per_investor': '$12M',
                'lead_investor': 'Andreessen Horowitz',
                'funding_timeline': 'Early Stage'
            }
        ]
        
        return seed_data[:max_results]

    def _get_pitchbook_seed_data(self, max_results: int) -> List[Dict]:
        """Fetch seed funding data from PitchBook (simulated)"""
        logger.info("Fetching seed funding data from PitchBook")
        
        seed_data = [
            {
                'startup_name': 'Starkware',
                'funding_amount': '$75M',
                'funding_round': 'Seed Extension',
                'announcement_date': '2023-08-01',
                'investors': ['Pantera Capital', 'Three Arrows Capital', 'Framework Ventures'],
                'num_investors': 3,
                'source_site': 'PitchBook',
                'source_url': 'https://pitchbook.com/companies/starkware',
                'description': 'Zero-knowledge proofs for Ethereum scaling',
                'headquarters': 'Tel Aviv, Israel',
                'industry': 'Blockchain/Layer 2',
                'investor_type': ['VC Firms', 'Hedge Funds'],
                'average_investment_per_investor': '$25M',
                'lead_investor': 'Pantera Capital',
                'funding_timeline': 'Early Stage'
            },
            {
                'startup_name': 'Solana Labs',
                'funding_amount': '$25M',
                'funding_round': 'Seed',
                'announcement_date': '2023-07-15',
                'investors': ['USV', 'Consensus Lab', 'Polychain Capital'],
                'num_investors': 3,
                'source_site': 'PitchBook',
                'source_url': 'https://pitchbook.com/companies/solana-labs',
                'description': 'High-speed blockchain network',
                'headquarters': 'San Francisco, USA',
                'industry': 'Blockchain',
                'investor_type': ['VC Firms'],
                'average_investment_per_investor': '$8.33M',
                'lead_investor': 'USV',
                'funding_timeline': 'Early Stage'
            }
        ]
        
        return seed_data[:max_results]

    def _get_techcrunch_seed_data(self, max_results: int) -> List[Dict]:
        """Fetch seed funding data from TechCrunch articles (simulated)"""
        logger.info("Fetching seed funding data from TechCrunch")
        
        seed_data = [
            {
                'startup_name': 'Arbitrum (Offchain Labs)',
                'funding_amount': '$23.3M',
                'funding_round': 'Seed Round',
                'announcement_date': '2023-09-10',
                'investors': ['Polychain Capital', 'Distributed Global', 'Longhash Ventures'],
                'num_investors': 3,
                'source_site': 'TechCrunch',
                'source_url': 'https://techcrunch.com/arbitrum-funding',
                'description': 'Layer 2 scaling solution for Ethereum',
                'headquarters': 'New York, USA',
                'industry': 'Blockchain/Layer 2',
                'investor_type': ['VC Firms'],
                'average_investment_per_investor': '$7.77M',
                'lead_investor': 'Polychain Capital',
                'funding_timeline': 'Early Stage'
            },
            {
                'startup_name': 'Aptos Labs',
                'funding_amount': '$12M',
                'funding_round': 'Seed',
                'announcement_date': '2023-08-25',
                'investors': ['FTX Ventures', 'Sequoia Capital', 'Katie Haun'],
                'num_investors': 3,
                'source_site': 'TechCrunch',
                'source_url': 'https://techcrunch.com/aptos-labs-funding',
                'description': 'Move-language blockchain platform',
                'headquarters': 'Palo Alto, USA',
                'industry': 'Blockchain',
                'investor_type': ['VC Firms', 'Angel Investors'],
                'average_investment_per_investor': '$4M',
                'lead_investor': 'FTX Ventures',
                'funding_timeline': 'Early Stage'
            }
        ]
        
        return seed_data[:max_results]

    def _get_cbinsights_seed_data(self, max_results: int) -> List[Dict]:
        """Fetch seed funding data from CB Insights (simulated)"""
        logger.info("Fetching seed funding data from CB Insights")
        
        seed_data = [
            {
                'startup_name': 'Polygon Studios',
                'funding_amount': '$30M',
                'funding_round': 'Seed',
                'announcement_date': '2023-09-05',
                'investors': ['Animoca Brands', 'Steady State Ventures', 'Makers Fund'],
                'num_investors': 3,
                'source_site': 'CB Insights',
                'source_url': 'https://www.cbinsights.com/company/polygon-studios',
                'description': 'Gaming and entertainment on Polygon blockchain',
                'headquarters': 'New York, USA',
                'industry': 'Gaming/NFT',
                'investor_type': ['VC Firms'],
                'average_investment_per_investor': '$10M',
                'lead_investor': 'Animoca Brands',
                'funding_timeline': 'Early Stage'
            },
            {
                'startup_name': 'Brave Software',
                'funding_amount': '$35M',
                'funding_round': 'Seed Round',
                'announcement_date': '2023-08-30',
                'investors': ['Foundation Capital', 'Pantera Capital', 'Digital Currency Group'],
                'num_investors': 3,
                'source_site': 'CB Insights',
                'source_url': 'https://www.cbinsights.com/company/brave-software',
                'description': 'Privacy-focused web browser with crypto integration',
                'headquarters': 'San Francisco, USA',
                'industry': 'Web3/Privacy',
                'investor_type': ['VC Firms'],
                'average_investment_per_investor': '$11.67M',
                'lead_investor': 'Foundation Capital',
                'funding_timeline': 'Early Stage'
            }
        ]
        
        return seed_data[:max_results]

    def calculate_investor_metrics(self, seed_funding_data: List[Dict]) -> Dict:
        """Calculate investor-focused metrics from seed funding data"""
        logger.info("Calculating investor metrics from seed funding data")
        
        metrics = {
            'total_seed_funding': 0,
            'average_seed_round_size': 0,
            'most_active_investors': [],
            'lead_investors_summary': {},
            'investor_investment_distribution': {},
            'source_site_summary': {},
            'total_unique_startups': len(seed_funding_data),
            'total_unique_investors': set(),
            'total_seed_rounds': len(seed_funding_data),
            'average_investors_per_round': 0,
            'industry_breakdown': {},
            'geographic_distribution': {}
        }
        
        from agent.processors.data_parser import DataParser
        
        total_investors_count = 0
        for round_data in seed_funding_data:
            # Calculate total funding
            funding_amount = DataParser.parse_funding_amount(round_data.get('funding_amount', '0'))
            if funding_amount:
                metrics['total_seed_funding'] += funding_amount
            
            # Track unique investors
            investors = round_data.get('investors', [])
            metrics['total_unique_investors'].update(investors)
            total_investors_count += len(investors)
            
            # Track source sites
            source_site = round_data.get('source_site', 'Unknown')
            if source_site not in metrics['source_site_summary']:
                metrics['source_site_summary'][source_site] = {
                    'funding_rounds': 0,
                    'total_funding': 0,
                    'unique_investors': set()
                }
            metrics['source_site_summary'][source_site]['funding_rounds'] += 1
            if funding_amount:
                metrics['source_site_summary'][source_site]['total_funding'] += funding_amount
            metrics['source_site_summary'][source_site]['unique_investors'].update(investors)
            
            # Track lead investors
            lead_investor = round_data.get('lead_investor', 'Unknown')
            if lead_investor not in metrics['lead_investors_summary']:
                metrics['lead_investors_summary'][lead_investor] = {
                    'investments': 0,
                    'total_invested': 0,
                    'average_investment': 0
                }
            metrics['lead_investors_summary'][lead_investor]['investments'] += 1
            if funding_amount:
                metrics['lead_investors_summary'][lead_investor]['total_invested'] += funding_amount
            
            # Track industry breakdown
            industry = round_data.get('industry', 'Unknown')
            if industry not in metrics['industry_breakdown']:
                metrics['industry_breakdown'][industry] = 0
            metrics['industry_breakdown'][industry] += 1
            
            # Track geographic distribution
            headquarters = round_data.get('headquarters', 'Unknown')
            if headquarters not in metrics['geographic_distribution']:
                metrics['geographic_distribution'][headquarters] = 0
            metrics['geographic_distribution'][headquarters] += 1
        
        # Calculate averages
        if metrics['total_seed_rounds'] > 0:
            metrics['average_seed_round_size'] = metrics['total_seed_funding'] / metrics['total_seed_rounds']
            metrics['average_investors_per_round'] = total_investors_count / metrics['total_seed_rounds']
        
        # Get most active investors
        from collections import Counter
        investor_list = []
        for round_data in seed_funding_data:
            investor_list.extend(round_data.get('investors', []))
        
        investor_counts = Counter(investor_list)
        metrics['most_active_investors'] = [
            {'investor': inv, 'participation_count': count}
            for inv, count in investor_counts.most_common(10)
        ]
        
        # Calculate average investment for lead investors
        for lead_investor in metrics['lead_investors_summary']:
            investments = metrics['lead_investors_summary'][lead_investor]['investments']
            total = metrics['lead_investors_summary'][lead_investor]['total_invested']
            if investments > 0:
                metrics['lead_investors_summary'][lead_investor]['average_investment'] = total / investments
        
        # Convert sets to lists for serialization
        metrics['total_unique_investors'] = list(metrics['total_unique_investors'])
        metrics['source_site_summary'] = {
            site: {
                'funding_rounds': data['funding_rounds'],
                'total_funding': data['total_funding'],
                'unique_investors': list(data['unique_investors'])
            }
            for site, data in metrics['source_site_summary'].items()
        }
        
        return metrics

    def generate_investor_report(self, seed_funding_data: List[Dict]) -> Dict:
        """Generate an investor-focused report with site names and key metrics"""
        logger.info("Generating investor-focused report")
        
        metrics = self.calculate_investor_metrics(seed_funding_data)
        
        report = {
            'report_type': 'Investor-Focused Seed Funding Analysis',
            'generation_date': datetime.now().isoformat(),
            'summary': {
                'total_seed_funding_raised': f"${metrics['total_seed_funding']:,.0f}",
                'average_seed_round_size': f"${metrics['average_seed_round_size']:,.0f}",
                'total_seed_rounds_tracked': metrics['total_seed_rounds'],
                'unique_investors_identified': len(metrics['total_unique_investors']),
                'average_investors_per_round': round(metrics['average_investors_per_round'], 2)
            },
            'investor_insights': {
                'most_active_investors': metrics['most_active_investors'],
                'lead_investors': metrics['lead_investors_summary'],
                'investor_distribution': metrics['investor_investment_distribution']
            },
            'source_analysis': metrics['source_site_summary'],
            'industry_breakdown': metrics['industry_breakdown'],
            'geographic_distribution': metrics['geographic_distribution'],
            'raw_data': seed_funding_data
        }
        
        return report
