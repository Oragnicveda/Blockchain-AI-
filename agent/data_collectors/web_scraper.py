import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from fake_useragent import UserAgent
from retry import retry
from agent.utils.logger import setup_logger
from agent.utils.config import Config

logger = setup_logger(__name__)


class WebScraper:
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
    
    @retry(tries=3, delay=2, backoff=2)
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=self.config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            time.sleep(self.config.RATE_LIMIT_DELAY)
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def scrape_startup_data(self, category: str, max_results: int = 50) -> List[Dict]:
        logger.info(f"Scraping startups for category: {category}")
        startups = []
        
        startups.extend(self._scrape_sample_data(category, max_results))
        
        logger.info(f"Collected {len(startups)} startups for {category}")
        return startups
    
    def _scrape_sample_data(self, category: str, max_results: int) -> List[Dict]:
        sample_startups = {
            'blockchain': [
                {
                    'name': 'Chainalysis',
                    'description': 'Blockchain data platform providing investigation and compliance tools',
                    'category': 'Blockchain',
                    'funding_amount': '$366M',
                    'funding_round': 'Series F',
                    'investors': ['Coatue', 'Addition', 'Ribbit Capital'],
                    'valuation': '$8.6B',
                    'founded_date': '2014',
                    'employee_count': '800+',
                    'headquarters': 'New York, USA',
                    'website': 'https://www.chainalysis.com',
                    'last_funding_date': '2022-05-10'
                },
                {
                    'name': 'Alchemy',
                    'description': 'Blockchain developer platform powering millions of users',
                    'category': 'Blockchain',
                    'funding_amount': '$200M',
                    'funding_round': 'Series C1',
                    'investors': ['Lightspeed', 'Silver Lake', 'a16z'],
                    'valuation': '$10.2B',
                    'founded_date': '2017',
                    'employee_count': '150+',
                    'headquarters': 'San Francisco, USA',
                    'website': 'https://www.alchemy.com',
                    'last_funding_date': '2022-02-08'
                },
                {
                    'name': 'Fireblocks',
                    'description': 'Digital asset custody and transfer platform',
                    'category': 'Blockchain',
                    'funding_amount': '$550M',
                    'funding_round': 'Series E',
                    'investors': ['Sequoia Capital', 'Stripes', 'Spark Capital'],
                    'valuation': '$8B',
                    'founded_date': '2018',
                    'employee_count': '600+',
                    'headquarters': 'New York, USA',
                    'website': 'https://www.fireblocks.com',
                    'last_funding_date': '2022-01-27'
                },
            ],
            'crypto': [
                {
                    'name': 'Circle',
                    'description': 'Financial services company and issuer of USDC stablecoin',
                    'category': 'Crypto',
                    'funding_amount': '$440M',
                    'funding_round': 'Series E',
                    'investors': ['FTX', 'Digital Currency Group', 'Fidelity'],
                    'valuation': '$9B',
                    'founded_date': '2013',
                    'employee_count': '850+',
                    'headquarters': 'Boston, USA',
                    'website': 'https://www.circle.com',
                    'last_funding_date': '2021-05-27'
                },
                {
                    'name': 'Blockchain.com',
                    'description': 'Cryptocurrency exchange and wallet provider',
                    'category': 'Crypto',
                    'funding_amount': '$620M',
                    'funding_round': 'Series D',
                    'investors': ['Lightspeed', 'Google Ventures', 'Virgin Group'],
                    'valuation': '$14B',
                    'founded_date': '2011',
                    'employee_count': '1000+',
                    'headquarters': 'London, UK',
                    'website': 'https://www.blockchain.com',
                    'last_funding_date': '2022-03-15'
                },
                {
                    'name': 'Kraken',
                    'description': 'Cryptocurrency exchange and bank',
                    'category': 'Crypto',
                    'funding_amount': '$130M',
                    'funding_round': 'Series B',
                    'investors': ['Hummingbird Ventures', 'Blockchain Capital'],
                    'valuation': '$10.8B',
                    'founded_date': '2011',
                    'employee_count': '3200+',
                    'headquarters': 'San Francisco, USA',
                    'website': 'https://www.kraken.com',
                    'last_funding_date': '2021-09-20'
                },
            ],
            'web3': [
                {
                    'name': 'Consensys',
                    'description': 'Ethereum software company building Web3 infrastructure',
                    'category': 'Web3',
                    'funding_amount': '$450M',
                    'funding_round': 'Series D',
                    'investors': ['ParaFi Capital', 'SoftBank', 'Microsoft'],
                    'valuation': '$7B',
                    'founded_date': '2014',
                    'employee_count': '900+',
                    'headquarters': 'Brooklyn, USA',
                    'website': 'https://consensys.net',
                    'last_funding_date': '2022-03-15'
                },
                {
                    'name': 'Dapper Labs',
                    'description': 'Web3 entertainment company behind NBA Top Shot and Flow blockchain',
                    'category': 'Web3',
                    'funding_amount': '$605M',
                    'funding_round': 'Series D',
                    'investors': ['Coatue', 'a16z', 'Google Ventures'],
                    'valuation': '$7.6B',
                    'founded_date': '2018',
                    'employee_count': '500+',
                    'headquarters': 'Vancouver, Canada',
                    'website': 'https://www.dapperlabs.com',
                    'last_funding_date': '2021-09-22'
                },
                {
                    'name': 'Immutable',
                    'description': 'Layer 2 scaling solution for NFTs on Ethereum',
                    'category': 'Web3',
                    'funding_amount': '$280M',
                    'funding_round': 'Series C',
                    'investors': ['Temasek', 'Tencent', 'Animoca Brands'],
                    'valuation': '$2.5B',
                    'founded_date': '2018',
                    'employee_count': '280+',
                    'headquarters': 'Sydney, Australia',
                    'website': 'https://www.immutable.com',
                    'last_funding_date': '2022-03-07'
                },
            ],
            'ai': [
                {
                    'name': 'Fetch.ai',
                    'description': 'AI and blockchain platform for autonomous economic agents',
                    'category': 'AI Web3',
                    'funding_amount': '$40M',
                    'funding_round': 'Series A',
                    'investors': ['DWF Labs', 'Outlier Ventures', 'Moonrock Capital'],
                    'valuation': '$500M',
                    'founded_date': '2017',
                    'employee_count': '120+',
                    'headquarters': 'Cambridge, UK',
                    'website': 'https://fetch.ai',
                    'last_funding_date': '2023-03-29'
                },
                {
                    'name': 'Ocean Protocol',
                    'description': 'Decentralized data exchange protocol combining AI and blockchain',
                    'category': 'AI Web3',
                    'funding_amount': '$38M',
                    'funding_round': 'ICO/Token Sale',
                    'investors': ['Outlier Ventures', 'NGC Ventures'],
                    'valuation': '$300M',
                    'founded_date': '2017',
                    'employee_count': '80+',
                    'headquarters': 'Singapore',
                    'website': 'https://oceanprotocol.com',
                    'last_funding_date': '2021-07-15'
                },
                {
                    'name': 'SingularityNET',
                    'description': 'Decentralized AI marketplace on blockchain',
                    'category': 'AI Web3',
                    'funding_amount': '$36M',
                    'funding_round': 'Token Sale',
                    'investors': ['Foundation Capital', 'Deeptech Ventures'],
                    'valuation': '$420M',
                    'founded_date': '2017',
                    'employee_count': '100+',
                    'headquarters': 'Amsterdam, Netherlands',
                    'website': 'https://singularitynet.io',
                    'last_funding_date': '2021-04-12'
                },
            ],
            'defi': [
                {
                    'name': 'Compound Labs',
                    'description': 'Decentralized finance protocol for algorithmic money markets',
                    'category': 'DeFi',
                    'funding_amount': '$133M',
                    'funding_round': 'Series C',
                    'investors': ['a16z', 'Polychain Capital', 'Bain Capital'],
                    'valuation': '$1.2B',
                    'founded_date': '2018',
                    'employee_count': '50+',
                    'headquarters': 'San Francisco, USA',
                    'website': 'https://compound.finance',
                    'last_funding_date': '2022-03-23'
                },
                {
                    'name': 'Aave',
                    'description': 'Decentralized lending and borrowing protocol',
                    'category': 'DeFi',
                    'funding_amount': '$25M',
                    'funding_round': 'Token Sale',
                    'investors': ['Blockchain Capital', 'Standard Crypto'],
                    'valuation': '$1.8B',
                    'founded_date': '2017',
                    'employee_count': '70+',
                    'headquarters': 'London, UK',
                    'website': 'https://aave.com',
                    'last_funding_date': '2020-07-20'
                },
            ],
            'nft': [
                {
                    'name': 'OpenSea',
                    'description': 'Leading NFT marketplace',
                    'category': 'NFT',
                    'funding_amount': '$423M',
                    'funding_round': 'Series C',
                    'investors': ['Paradigm', 'Coatue', 'a16z'],
                    'valuation': '$13.3B',
                    'founded_date': '2017',
                    'employee_count': '230+',
                    'headquarters': 'New York, USA',
                    'website': 'https://opensea.io',
                    'last_funding_date': '2022-01-04'
                },
                {
                    'name': 'Magic Eden',
                    'description': 'Multi-chain NFT marketplace',
                    'category': 'NFT',
                    'funding_amount': '$160M',
                    'funding_round': 'Series B',
                    'investors': ['Electric Capital', 'Sequoia Capital', 'Paradigm'],
                    'valuation': '$1.6B',
                    'founded_date': '2021',
                    'employee_count': '150+',
                    'headquarters': 'San Francisco, USA',
                    'website': 'https://magiceden.io',
                    'last_funding_date': '2022-06-21'
                },
            ]
        }
        
        category_lower = category.lower()
        if category_lower in sample_startups:
            return sample_startups[category_lower][:max_results]
        
        all_startups = []
        for startups_list in sample_startups.values():
            all_startups.extend(startups_list)
        return all_startups[:max_results]
