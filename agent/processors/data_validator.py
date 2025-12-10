from typing import Dict, List
from agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class DataValidator:
    REQUIRED_FIELDS = ['name', 'category', 'funding_amount']
    
    @staticmethod
    def validate_startup(startup: Dict) -> bool:
        for field in DataValidator.REQUIRED_FIELDS:
            if field not in startup or not startup[field]:
                logger.warning(f"Missing required field '{field}' for startup: {startup.get('name', 'Unknown')}")
                return False
        
        return True
    
    @staticmethod
    def validate_url(url: str) -> bool:
        import re
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None
    
    @staticmethod
    def validate_date(date_str: str) -> bool:
        import re
        
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{4}$',
            r'^\d{2}/\d{2}/\d{4}$',
        ]
        
        return any(re.match(pattern, date_str) for pattern in date_patterns)
    
    @staticmethod
    def filter_valid_startups(startups: List[Dict]) -> List[Dict]:
        valid_startups = []
        
        for startup in startups:
            if DataValidator.validate_startup(startup):
                valid_startups.append(startup)
        
        logger.info(f"Validated {len(valid_startups)} out of {len(startups)} startups")
        return valid_startups
    
    @staticmethod
    def deduplicate_startups(startups: List[Dict]) -> List[Dict]:
        seen_names = set()
        unique_startups = []
        
        for startup in startups:
            name = startup.get('name', '').lower()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_startups.append(startup)
        
        logger.info(f"Removed {len(startups) - len(unique_startups)} duplicates")
        return unique_startups
