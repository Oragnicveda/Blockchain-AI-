import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from agent.data_collectors import WebScraper, APIClient, NewsAggregator
from agent.processors import DataParser, DataValidator
from agent.utils.logger import setup_logger
from agent.utils.config import Config

logger = setup_logger(__name__)


class StartupResearchAgent:
    def __init__(self):
        self.config = Config()
        self.config.validate()
        
        self.web_scraper = WebScraper()
        self.api_client = APIClient()
        self.news_aggregator = NewsAggregator()
        self.data_parser = DataParser()
        self.data_validator = DataValidator()
        
        logger.info("Startup Research Agent initialized")
    
    def research_startups(
        self,
        categories: Optional[List[str]] = None,
        max_results: int = 50,
        include_news: bool = True
    ) -> List[Dict]:
        if categories is None:
            categories = self.config.CATEGORIES
        
        logger.info(f"Starting research for categories: {categories}")
        logger.info(f"Maximum results per category: {max_results}")
        
        all_startups = []
        
        for category in categories:
            logger.info(f"\n{'='*60}")
            logger.info(f"Researching {category.upper()} startups")
            logger.info(f"{'='*60}")
            
            category_startups = self._collect_category_data(category, max_results)
            all_startups.extend(category_startups)
            
            if include_news:
                news_data = self.news_aggregator.fetch_funding_news(category)
                logger.info(f"Found {len(news_data)} news articles for {category}")
        
        all_startups = self.data_validator.deduplicate_startups(all_startups)
        all_startups = self.data_validator.filter_valid_startups(all_startups)
        
        all_startups = self._enrich_data(all_startups)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Research complete! Total startups collected: {len(all_startups)}")
        logger.info(f"{'='*60}\n")
        
        return all_startups
    
    def _collect_category_data(self, category: str, max_results: int) -> List[Dict]:
        startups = []
        
        logger.info("Collecting data from web sources...")
        web_data = self.web_scraper.scrape_startup_data(category, max_results)
        startups.extend(web_data)
        
        logger.info("Collecting data from APIs...")
        api_data = self.api_client.fetch_crunchbase_data(category, max_results)
        startups.extend(api_data)
        
        cleaned_startups = []
        for startup in startups:
            cleaned = self.data_parser.clean_startup_data(startup)
            cleaned_startups.append(cleaned)
        
        return cleaned_startups
    
    def _enrich_data(self, startups: List[Dict]) -> List[Dict]:
        logger.info("Enriching startup data...")
        
        enriched_startups = []
        
        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            futures = {
                executor.submit(self.api_client.enrich_startup_data, startup): startup
                for startup in startups
            }
            
            for future in tqdm(as_completed(futures), total=len(futures), desc="Enriching data"):
                try:
                    enriched = future.result()
                    enriched_startups.append(enriched)
                except Exception as e:
                    startup = futures[future]
                    logger.error(f"Error enriching {startup.get('name')}: {str(e)}")
                    enriched_startups.append(startup)
        
        return enriched_startups
    
    def export_results(
        self,
        startups: List[Dict],
        format: str = 'json',
        filename: Optional[str] = None
    ) -> str:
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'startups_{timestamp}'
        
        output_path = self.config.OUTPUT_DIR / f'{filename}.{format}'
        
        logger.info(f"Exporting {len(startups)} startups to {output_path}")
        
        if format == 'json':
            self._export_json(startups, output_path)
        elif format == 'csv':
            self._export_csv(startups, output_path)
        elif format == 'xlsx' or format == 'excel':
            self._export_excel(startups, output_path.with_suffix('.xlsx'))
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Export complete: {output_path}")
        return str(output_path)
    
    def _export_json(self, startups: List[Dict], path: Path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(startups, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, startups: List[Dict], path: Path):
        df = pd.DataFrame(startups)
        
        if 'investors' in df.columns:
            df['investors'] = df['investors'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x
            )
        
        df.to_csv(path, index=False, encoding='utf-8')
    
    def _export_excel(self, startups: List[Dict], path: Path):
        df = pd.DataFrame(startups)
        
        if 'investors' in df.columns:
            df['investors'] = df['investors'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x
            )
        
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Startups', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Startups']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def generate_summary(self, startups: List[Dict]) -> Dict:
        logger.info("Generating summary statistics...")
        
        df = pd.DataFrame(startups)
        
        summary = {
            'total_startups': len(startups),
            'categories': {},
            'total_funding_collected': 0,
            'average_funding': 0,
            'top_funded_startups': [],
            'top_investors': [],
            'countries': {},
        }
        
        if 'category' in df.columns:
            summary['categories'] = df['category'].value_counts().to_dict()
        
        if 'headquarters' in df.columns:
            for hq in df['headquarters'].dropna():
                if isinstance(hq, str) and ',' in hq:
                    country = hq.split(',')[-1].strip()
                    summary['countries'][country] = summary['countries'].get(country, 0) + 1
        
        funding_amounts = []
        for startup in startups:
            amount_str = startup.get('funding_amount', '')
            if amount_str:
                amount = self.data_parser.parse_funding_amount(str(amount_str))
                if amount:
                    funding_amounts.append(amount)
        
        if funding_amounts:
            summary['total_funding_collected'] = sum(funding_amounts)
            summary['average_funding'] = sum(funding_amounts) / len(funding_amounts)
        
        sorted_startups = sorted(
            startups,
            key=lambda x: self.data_parser.parse_funding_amount(str(x.get('funding_amount', '0'))) or 0,
            reverse=True
        )
        summary['top_funded_startups'] = [
            {
                'name': s.get('name'),
                'funding': s.get('funding_amount'),
                'valuation': s.get('valuation')
            }
            for s in sorted_startups[:10]
        ]
        
        all_investors = []
        for startup in startups:
            investors = startup.get('investors', [])
            if isinstance(investors, list):
                all_investors.extend(investors)
        
        from collections import Counter
        investor_counts = Counter(all_investors)
        summary['top_investors'] = [
            {'name': inv, 'investments': count}
            for inv, count in investor_counts.most_common(10)
        ]
        
        return summary
    
    def print_summary(self, startups: List[Dict]):
        summary = self.generate_summary(startups)
        
        print("\n" + "="*80)
        print("STARTUP RESEARCH SUMMARY")
        print("="*80)
        print(f"\nTotal Startups: {summary['total_startups']}")
        
        if summary['categories']:
            print("\nStartups by Category:")
            for category, count in summary['categories'].items():
                print(f"  - {category}: {count}")
        
        if summary['total_funding_collected']:
            print(f"\nTotal Funding Collected: ${summary['total_funding_collected']:,.0f}")
            print(f"Average Funding per Startup: ${summary['average_funding']:,.0f}")
        
        if summary['top_funded_startups']:
            print("\nTop 10 Funded Startups:")
            for i, startup in enumerate(summary['top_funded_startups'][:10], 1):
                print(f"  {i}. {startup['name']} - {startup['funding']} (Valuation: {startup.get('valuation', 'N/A')})")
        
        if summary['top_investors']:
            print("\nTop 10 Active Investors:")
            for i, investor in enumerate(summary['top_investors'][:10], 1):
                print(f"  {i}. {investor['name']} - {investor['investments']} investments")
        
        if summary['countries']:
            print("\nStartups by Country:")
            for country, count in sorted(summary['countries'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {country}: {count}")
        
        print("\n" + "="*80 + "\n")
