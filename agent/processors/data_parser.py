import re
from typing import Dict, Optional, List
from agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataParser:
    @staticmethod
    def parse_funding_amount(amount_str: str) -> Optional[float]:
        try:
            amount_str = amount_str.upper().replace('$', '').replace(',', '').strip()
            
            multipliers = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}
            
            for suffix, multiplier in multipliers.items():
                if suffix in amount_str:
                    number = float(amount_str.replace(suffix, '').strip())
                    return number * multiplier
            
            return float(amount_str)
        except:
            logger.warning(f"Could not parse funding amount: {amount_str}")
            return None
    
    @staticmethod
    def parse_employee_count(count_str: str) -> Optional[int]:
        try:
            count_str = count_str.replace(',', '').replace('+', '').strip()
            
            match = re.search(r'(\d+)', count_str)
            if match:
                return int(match.group(1))
            return None
        except:
            logger.warning(f"Could not parse employee count: {count_str}")
            return None
    
    @staticmethod
    def parse_valuation(valuation_str: str) -> Optional[float]:
        return DataParser.parse_funding_amount(valuation_str)
    
    @staticmethod
    def normalize_category(category: str) -> str:
        category_mapping = {
            'blockchain': 'Blockchain',
            'crypto': 'Crypto',
            'cryptocurrency': 'Crypto',
            'web3': 'Web3',
            'ai': 'AI Web3',
            'defi': 'DeFi',
            'nft': 'NFT',
            'decentralized finance': 'DeFi',
        }
        
        return category_mapping.get(category.lower(), category.title())
    
    @staticmethod
    def extract_investors(investors_data: any) -> List[str]:
        if isinstance(investors_data, list):
            return investors_data
        elif isinstance(investors_data, str):
            return [inv.strip() for inv in investors_data.split(',')]
        return []
    
    @staticmethod
    def clean_startup_data(startup: Dict) -> Dict:
        cleaned = {}
        
        field_cleaners = {
            'name': lambda x: x.strip() if isinstance(x, str) else x,
            'description': lambda x: x.strip() if isinstance(x, str) else x,
            'category': DataParser.normalize_category,
            'funding_amount': lambda x: x if isinstance(x, str) else str(x),
            'funding_round': lambda x: x.strip() if isinstance(x, str) else x,
            'investors': DataParser.extract_investors,
            'valuation': lambda x: x if isinstance(x, str) else str(x),
            'founded_date': lambda x: x.strip() if isinstance(x, str) else x,
            'employee_count': lambda x: x if isinstance(x, str) else str(x),
            'headquarters': lambda x: x.strip() if isinstance(x, str) else x,
            'website': lambda x: x.strip() if isinstance(x, str) else x,
            'last_funding_date': lambda x: x.strip() if isinstance(x, str) else x,
        }
        
        for field, cleaner in field_cleaners.items():
            if field in startup:
                try:
                    cleaned[field] = cleaner(startup[field])
                except Exception as e:
                    logger.warning(f"Error cleaning field {field}: {str(e)}")
                    cleaned[field] = startup[field]
            else:
                cleaned[field] = None
        
        for key, value in startup.items():
            if key not in cleaned:
                cleaned[key] = value
        
        return cleaned
