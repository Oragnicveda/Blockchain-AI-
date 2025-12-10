import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from agent.data_collectors import WebScraper, APIClient, NewsAggregator, SeedFundingCollector
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
        self.seed_funding_collector = SeedFundingCollector()
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
    
    def research_seed_funding(
        self,
        max_results: int = 50,
        generate_investor_report: bool = True
    ) -> tuple:
        """
        Research seed funding rounds from crypto startups with investor-focused metrics.
        
        Returns:
            tuple: (seed_funding_data, investor_report_data)
        """
        logger.info(f"\n{'='*60}")
        logger.info("SEED FUNDING RESEARCH - CRYPTO STARTUPS")
        logger.info(f"{'='*60}")
        
        seed_funding_data = self.seed_funding_collector.collect_seed_funding_data(max_results)
        
        logger.info(f"Collected {len(seed_funding_data)} seed funding rounds")
        
        investor_report = None
        if generate_investor_report:
            investor_report = self.seed_funding_collector.generate_investor_report(seed_funding_data)
            logger.info("Investor-focused report generated successfully")
        
        logger.info(f"{'='*60}\n")
        
        return seed_funding_data, investor_report
    
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
        elif format == 'txt' or format == 'text':
            self._export_txt(startups, output_path.with_suffix('.txt'))
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Export complete: {output_path}")
        return str(output_path)
    
    def export_seed_funding_results(
        self,
        seed_funding_data: List[Dict],
        investor_report: Optional[Dict] = None,
        format: str = 'json',
        filename: Optional[str] = None
    ) -> str:
        """Export seed funding data and investor report"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'seed_funding_{timestamp}'
        
        output_path = self.config.OUTPUT_DIR / f'{filename}.{format}'
        
        logger.info(f"Exporting seed funding data ({len(seed_funding_data)} rounds) to {output_path}")
        
        if format == 'json':
            export_data = {
                'seed_funding_rounds': seed_funding_data,
                'investor_report': investor_report
            }
            self._export_json(export_data, output_path)
        elif format == 'csv':
            self._export_csv(seed_funding_data, output_path)
        elif format == 'xlsx' or format == 'excel':
            self._export_seed_funding_excel(seed_funding_data, investor_report, output_path.with_suffix('.xlsx'))
        elif format == 'txt' or format == 'text':
            self._export_seed_funding_txt(seed_funding_data, investor_report, output_path.with_suffix('.txt'))
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
    
    def _export_txt(self, startups: List[Dict], path: Path):
        """Export startups data in human-readable text format"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("STARTUP RESEARCH RESULTS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Startups: {len(startups)}\n")
            f.write("=" * 80 + "\n\n")
            
            for idx, startup in enumerate(startups, 1):
                f.write(f"\n{'#' * 80}\n")
                f.write(f"STARTUP #{idx}\n")
                f.write(f"{'#' * 80}\n\n")
                
                f.write(f"Name: {startup.get('name', 'N/A')}\n")
                f.write(f"Category: {startup.get('category', 'N/A')}\n")
                f.write(f"Description: {startup.get('description', 'N/A')}\n")
                f.write(f"\nFunding Information:\n")
                f.write(f"  Funding Amount: {startup.get('funding_amount', 'N/A')}\n")
                f.write(f"  Funding Round: {startup.get('funding_round', 'N/A')}\n")
                f.write(f"  Valuation: {startup.get('valuation', 'N/A')}\n")
                f.write(f"  Date: {startup.get('funding_date', 'N/A')}\n")
                
                investors = startup.get('investors', [])
                if investors and isinstance(investors, list):
                    f.write(f"\nInvestors ({len(investors)}):\n")
                    for inv in investors:
                        f.write(f"  - {inv}\n")
                elif investors:
                    f.write(f"\nInvestors: {investors}\n")
                
                f.write(f"\nCompany Details:\n")
                f.write(f"  Website: {startup.get('website', 'N/A')}\n")
                f.write(f"  Headquarters: {startup.get('headquarters', 'N/A')}\n")
                f.write(f"  Founded: {startup.get('founded_date', 'N/A')}\n")
                f.write(f"  Employees: {startup.get('num_employees', 'N/A')}\n")
                
                founders = startup.get('founders', [])
                if founders and isinstance(founders, list):
                    f.write(f"\nFounders:\n")
                    for founder in founders:
                        f.write(f"  - {founder}\n")
                elif founders:
                    f.write(f"\nFounders: {founders}\n")
                
                if startup.get('source_url'):
                    f.write(f"\nSource: {startup.get('source_url')}\n")
                
                f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
    
    def _export_seed_funding_excel(self, seed_funding_data: List[Dict], investor_report: Optional[Dict], path: Path):
        """Export seed funding data with investor report to Excel with multiple sheets"""
        df_seed = pd.DataFrame(seed_funding_data)
        
        # Convert lists to strings for Excel
        if 'investors' in df_seed.columns:
            df_seed['investors'] = df_seed['investors'].apply(
                lambda x: ', '.join(x) if isinstance(x, list) else x
            )
        
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df_seed.to_excel(writer, sheet_name='Seed Funding Rounds', index=False)
            
            # Add investor report sheets if available
            if investor_report:
                summary = investor_report.get('summary', {})
                df_summary = pd.DataFrame([summary])
                df_summary.to_excel(writer, sheet_name='Summary', index=False)
                
                # Add investor insights
                investors = investor_report.get('investor_insights', {}).get('most_active_investors', [])
                if investors:
                    df_investors = pd.DataFrame(investors)
                    df_investors.to_excel(writer, sheet_name='Most Active Investors', index=False)
                
                # Add source analysis
                source_analysis = investor_report.get('source_analysis', {})
                if source_analysis:
                    source_data = []
                    for site, data in source_analysis.items():
                        source_data.append({
                            'Source Site': site,
                            'Funding Rounds': data.get('funding_rounds', 0),
                            'Total Funding': f"${data.get('total_funding', 0):,.0f}",
                            'Unique Investors': len(data.get('unique_investors', []))
                        })
                    df_sources = pd.DataFrame(source_data)
                    df_sources.to_excel(writer, sheet_name='Source Analysis', index=False)
            
            # Auto-adjust column widths
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _export_seed_funding_txt(self, seed_funding_data: List[Dict], investor_report: Optional[Dict], path: Path):
        """Export seed funding data and investor report in human-readable text format"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SEED FUNDING ANALYSIS - INVESTOR-FOCUSED REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            if investor_report:
                summary = investor_report.get('summary', {})
                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 80 + "\n")
                f.write(f"Total Seed Funding Raised: {summary.get('total_seed_funding_raised', 'N/A')}\n")
                f.write(f"Average Seed Round Size: {summary.get('average_seed_round_size', 'N/A')}\n")
                f.write(f"Total Seed Rounds Tracked: {summary.get('total_seed_rounds_tracked', 0)}\n")
                f.write(f"Unique Investors Identified: {summary.get('unique_investors_identified', 0)}\n")
                f.write(f"Average Investors per Round: {summary.get('average_investors_per_round', 0):.1f}\n")
                f.write("\n")
                
                investors = investor_report.get('investor_insights', {}).get('most_active_investors', [])
                if investors:
                    f.write("MOST ACTIVE INVESTORS (TOP 20)\n")
                    f.write("-" * 80 + "\n")
                    for i, inv in enumerate(investors[:20], 1):
                        f.write(f"{i:2d}. {inv['investor']:<50} {inv['participation_count']} participations\n")
                    f.write("\n")
                
                lead_investors = investor_report.get('investor_insights', {}).get('lead_investors', {})
                if lead_investors:
                    f.write("LEAD INVESTORS SUMMARY\n")
                    f.write("-" * 80 + "\n")
                    sorted_leads = sorted(lead_investors.items(), key=lambda x: x[1]['investments'], reverse=True)[:15]
                    for investor, data in sorted_leads:
                        f.write(f"\nInvestor: {investor}\n")
                        f.write(f"  Investments: {data['investments']}\n")
                        f.write(f"  Total Invested: ${data['total_invested']:,.0f}\n")
                        f.write(f"  Average Investment: ${data['average_investment']:,.0f}\n")
                    f.write("\n")
                
                source_analysis = investor_report.get('source_analysis', {})
                if source_analysis:
                    f.write("FUNDING DATA SOURCES\n")
                    f.write("-" * 80 + "\n")
                    for site, data in sorted(source_analysis.items(), key=lambda x: x[1]['total_funding'], reverse=True):
                        f.write(f"\nSource: {site}\n")
                        f.write(f"  Funding Rounds: {data['funding_rounds']}\n")
                        f.write(f"  Total Funding: ${data['total_funding']:,.0f}\n")
                        f.write(f"  Unique Investors: {len(data['unique_investors'])}\n")
                        if data['unique_investors']:
                            f.write(f"  Top Investors: {', '.join(list(data['unique_investors'])[:5])}\n")
                    f.write("\n")
                
                industry = investor_report.get('industry_breakdown', {})
                if industry:
                    f.write("INDUSTRY BREAKDOWN\n")
                    f.write("-" * 80 + "\n")
                    for ind, count in sorted(industry.items(), key=lambda x: x[1], reverse=True):
                        f.write(f"  {ind:<40} {count} startups\n")
                    f.write("\n")
                
                geography = investor_report.get('geographic_distribution', {})
                if geography:
                    f.write("GEOGRAPHIC DISTRIBUTION\n")
                    f.write("-" * 80 + "\n")
                    for location, count in sorted(geography.items(), key=lambda x: x[1], reverse=True)[:15]:
                        f.write(f"  {location:<40} {count} startups\n")
                    f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("DETAILED SEED FUNDING ROUNDS\n")
            f.write("=" * 80 + "\n\n")
            
            for idx, funding_round in enumerate(seed_funding_data, 1):
                f.write(f"\n{'#' * 80}\n")
                f.write(f"FUNDING ROUND #{idx}\n")
                f.write(f"{'#' * 80}\n\n")
                
                f.write(f"Startup: {funding_round.get('startup_name', 'N/A')}\n")
                f.write(f"Industry: {funding_round.get('industry', 'N/A')}\n")
                f.write(f"Headquarters: {funding_round.get('headquarters', 'N/A')}\n")
                f.write(f"Description: {funding_round.get('description', 'N/A')}\n")
                
                f.write(f"\nFunding Details:\n")
                funding_amount = funding_round.get('funding_amount', 0)
                if isinstance(funding_amount, (int, float)):
                    f.write(f"  Amount: ${funding_amount:,.0f}\n")
                else:
                    f.write(f"  Amount: {funding_amount}\n")
                f.write(f"  Round: {funding_round.get('funding_round', 'N/A')}\n")
                f.write(f"  Announcement Date: {funding_round.get('announcement_date', 'N/A')}\n")
                f.write(f"  Timeline: {funding_round.get('funding_timeline', 'N/A')}\n")
                
                investors = funding_round.get('investors', [])
                num_investors = funding_round.get('num_investors', 0)
                lead_investor = funding_round.get('lead_investor', 'N/A')
                
                f.write(f"\nInvestor Information:\n")
                f.write(f"  Total Investors: {num_investors}\n")
                f.write(f"  Lead Investor: {lead_investor}\n")
                f.write(f"  Investor Type: {funding_round.get('investor_type', 'N/A')}\n")
                avg_investment = funding_round.get('average_investment_per_investor', 0)
                if isinstance(avg_investment, (int, float)):
                    f.write(f"  Average Investment per Investor: ${avg_investment:,.0f}\n")
                else:
                    f.write(f"  Average Investment per Investor: {avg_investment}\n")
                
                if investors and isinstance(investors, list):
                    f.write(f"\n  All Investors ({len(investors)}):\n")
                    for inv in investors:
                        f.write(f"    - {inv}\n")
                elif investors:
                    f.write(f"\n  Investors: {investors}\n")
                
                f.write(f"\nData Source:\n")
                f.write(f"  Site: {funding_round.get('source_site', 'N/A')}\n")
                f.write(f"  URL: {funding_round.get('source_url', 'N/A')}\n")
                
                f.write("\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF SEED FUNDING REPORT\n")
            f.write("=" * 80 + "\n")
    
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
    
    def print_seed_funding_summary(self, investor_report: Dict):
        """Print investor-focused seed funding summary with site names"""
        if not investor_report:
            logger.warning("No investor report available")
            return
        
        print("\n" + "="*80)
        print("SEED FUNDING ANALYSIS - INVESTOR PERSPECTIVE")
        print("="*80)
        
        summary = investor_report.get('summary', {})
        print(f"\nTotal Seed Funding Raised: {summary.get('total_seed_funding_raised', 'N/A')}")
        print(f"Average Seed Round Size: {summary.get('average_seed_round_size', 'N/A')}")
        print(f"Total Seed Rounds Tracked: {summary.get('total_seed_rounds_tracked', 0)}")
        print(f"Unique Investors Identified: {summary.get('unique_investors_identified', 0)}")
        print(f"Average Investors per Round: {summary.get('average_investors_per_round', 0)}")
        
        # Most active investors
        investors = investor_report.get('investor_insights', {}).get('most_active_investors', [])
        if investors:
            print("\nMost Active Investors (Top 10):")
            for i, inv in enumerate(investors[:10], 1):
                print(f"  {i}. {inv['investor']} - {inv['participation_count']} participations")
        
        # Lead investors
        lead_investors = investor_report.get('investor_insights', {}).get('lead_investors', {})
        if lead_investors:
            print("\nLead Investors Summary:")
            for investor, data in sorted(lead_investors.items(), key=lambda x: x[1]['investments'], reverse=True)[:10]:
                print(f"  - {investor}: {data['investments']} investments, Total: ${data['total_invested']:,.0f}, Avg: ${data['average_investment']:,.0f}")
        
        # Source analysis with site names
        source_analysis = investor_report.get('source_analysis', {})
        if source_analysis:
            print("\nFunding Data Sources (Site Names):")
            for site, data in sorted(source_analysis.items(), key=lambda x: x[1]['total_funding'], reverse=True):
                print(f"  - {site}:")
                print(f"      Funding Rounds: {data['funding_rounds']}")
                print(f"      Total Funding: ${data['total_funding']:,.0f}")
                print(f"      Unique Investors: {len(data['unique_investors'])}")
        
        # Industry breakdown
        industry = investor_report.get('industry_breakdown', {})
        if industry:
            print("\nIndustry Breakdown:")
            for ind, count in sorted(industry.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {ind}: {count} startups")
        
        # Geographic distribution
        geography = investor_report.get('geographic_distribution', {})
        if geography:
            print("\nGeographic Distribution (Top 10):")
            for location, count in sorted(geography.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  - {location}: {count} startups")
        
        print("\n" + "="*80 + "\n")
