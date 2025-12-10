import requests
from typing import List, Dict, Optional
from agent.utils.logger import setup_logger
from agent.utils.config import Config

logger = setup_logger(__name__)


class APIClient:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        
    def fetch_crunchbase_data(self, category: str, max_results: int = 50) -> List[Dict]:
        if not self.config.CRUNCHBASE_API_KEY:
            logger.warning("Crunchbase API key not configured. Skipping API data collection.")
            return []
        
        logger.info(f"Fetching Crunchbase data for category: {category}")
        
        try:
            headers = {
                'X-cb-user-key': self.config.CRUNCHBASE_API_KEY,
                'Content-Type': 'application/json'
            }
            
            params = {
                'category_groups': category,
                'funding_total': 'positive',
                'limit': max_results
            }
            
            logger.info("Crunchbase API integration would fetch data here")
            return []
            
        except Exception as e:
            logger.error(f"Error fetching Crunchbase data: {str(e)}")
            return []
    
    def fetch_additional_company_data(self, company_name: str) -> Optional[Dict]:
        logger.info(f"Fetching additional data for: {company_name}")
        return None
    
    def enrich_startup_data(self, startup: Dict) -> Dict:
        logger.debug(f"Enriching data for {startup.get('name', 'Unknown')}")
        
        if 'social_media' not in startup:
            startup['social_media'] = {
                'twitter': f"https://twitter.com/{startup.get('name', '').lower().replace(' ', '')}",
                'linkedin': f"https://linkedin.com/company/{startup.get('name', '').lower().replace(' ', '-')}"
            }
        
        return startup
