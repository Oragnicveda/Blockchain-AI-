from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.dqda.data_collectors import (
    FounderBackgroundCollector,
    PitchDeckParser,
    TokenomicsCollector,
    WebsiteCrawler,
    WhitepaperProcessor,
)
from agent.dqda.data_collectors.base_collector import DQDADataPoint
from agent.utils.config import Config
from agent.utils.logger import setup_logger

logger = setup_logger(__name__)


class DQDAAgent:
    """End-to-end DQDA orchestration: collect, analyze, and produce a scoring dashboard."""

    def __init__(
        self,
        *,
        pitch_deck_parser: Optional[Any] = None,
        whitepaper_processor: Optional[Any] = None,
        website_crawler: Optional[Any] = None,
        tokenomics_collector: Optional[Any] = None,
        founder_background_collector: Optional[Any] = None,
        config: Optional[Config] = None,
    ):
        self.config = config or Config()
        self.config.validate()

        self.pitch_deck_parser = pitch_deck_parser or PitchDeckParser()
        self.whitepaper_processor = whitepaper_processor or WhitepaperProcessor()
        self.website_crawler = website_crawler or WebsiteCrawler()
        self.tokenomics_collector = tokenomics_collector or TokenomicsCollector()
        self.founder_background_collector = founder_background_collector or FounderBackgroundCollector()

    async def run_full_pipeline(
        self,
        *,
        startup_name: str,
        keywords: List[str],
        max_results: int = 5,
        website_urls: Optional[List[str]] = None,
        tokenomics_use_test_data: bool = False,
    ) -> Dict[str, Any]:
        """Run all collectors in parallel and return a consolidated report."""

        website_urls = website_urls or []

        tasks = {
            'pitch_deck': self.pitch_deck_parser.collect_data(
                startup_name=startup_name,
                keywords=keywords,
                max_results=max_results,
            ),
            'whitepaper': self.whitepaper_processor.collect_data(
                startup_name=startup_name,
                keywords=keywords,
                max_results=max_results,
            ),
            'website': self.website_crawler.collect_data(
                startup_name=startup_name,
                keywords=keywords,
                max_results=max_results,
                base_urls=website_urls,
            ),
            'tokenomics': self.tokenomics_collector.collect_data(
                startup_name=startup_name,
                keywords=keywords,
                max_results=max_results,
                use_test_data=tokenomics_use_test_data,
            ),
            'founders': self.founder_background_collector.collect_data(
                startup_name=startup_name,
                keywords=keywords,
                max_results=max_results,
            ),
        }

        logger.info(
            "Running DQDA pipeline for %s with %d collectors",
            startup_name,
            len(tasks),
        )

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        collected: Dict[str, List[DQDADataPoint]] = {}
        for key, value in zip(tasks.keys(), results):
            if isinstance(value, Exception):
                logger.warning("Collector %s failed: %s", key, str(value))
                collected[key] = []
            else:
                collected[key] = value

        founder_score = self._compute_founder_score(collected['founders'])
        market_analysis = self._compute_market_analysis(
            pitch_decks=collected['pitch_deck'],
            whitepapers=collected['whitepaper'],
            websites=collected['website'],
        )
        competition = self._compute_competition(
            pitch_decks=collected['pitch_deck'],
            websites=collected['website'],
        )
        token_utility = self._compute_token_utility(collected['tokenomics'])
        weaknesses = self._identify_weaknesses(
            founder_score=founder_score,
            market_analysis=market_analysis,
            competition=competition,
            token_utility=token_utility,
            collected=collected,
        )
        investor_fit = self._compute_investor_fit(
            founder_score=founder_score,
            market_score=float(market_analysis.get('score', 0.0)),
            competition_score=float(competition.get('score', 0.0)),
            token_score=float(token_utility.get('score', 0.0)),
            weaknesses=weaknesses,
        )

        report: Dict[str, Any] = {
            'startup_name': startup_name,
            'keywords': keywords,
            'collection_timestamp': datetime.now(timezone.utc).isoformat(),
            'founder_score': founder_score,
            'market_analysis': market_analysis,
            'competition': competition,
            'token_utility': token_utility,
            'weaknesses': weaknesses,
            'investor_fit': investor_fit,
            'data_points': {
                key: [dp.to_dict() for dp in points]
                for key, points in collected.items()
            },
        }

        return report

    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print a concise multi-metric summary for CLI use."""

        print("\n" + "=" * 80)
        print("DQDA SCORING SUMMARY")
        print("=" * 80)
        print(f"Startup: {report.get('startup_name')}")
        print(f"Founder score: {report.get('founder_score')} / 100")

        market = report.get('market_analysis', {})
        competition = report.get('competition', {})
        token = report.get('token_utility', {})
        investor = report.get('investor_fit', {})

        print(f"Market score: {market.get('score', 0)} / 100")
        print(f"Competition score: {competition.get('score', 0)} / 100")
        print(f"Token utility score: {token.get('score', 0)} / 100")
        print(f"Investor fit: {investor.get('score', 0)} / 100 ({investor.get('rating', 'n/a')})")

        weaknesses = report.get('weaknesses', [])
        if weaknesses:
            print("\nTop weaknesses:")
            for w in weaknesses[:5]:
                print(f"  - {w}")

        print("=" * 80 + "\n")

    def _compute_founder_score(self, founders: List[DQDADataPoint]) -> int:
        if not founders:
            return 0

        scores: List[float] = []
        for dp in founders:
            assessment = (dp.structured_data or {}).get('overall_assessment', {})
            if isinstance(assessment, dict) and isinstance(assessment.get('overall_score'), (int, float)):
                scores.append(float(assessment['overall_score']))
            else:
                scores.append(float(dp.confidence_score))

        avg = sum(scores) / len(scores) if scores else 0.0
        return int(round(max(0.0, min(1.0, avg)) * 100))

    def _compute_market_analysis(
        self,
        *,
        pitch_decks: List[DQDADataPoint],
        whitepapers: List[DQDADataPoint],
        websites: List[DQDADataPoint],
    ) -> Dict[str, Any]:
        signals: List[str] = []

        has_market_section = False
        section_coverage = 0.0
        for dp in pitch_decks:
            sections = (dp.structured_data or {}).get('sections', {})
            if isinstance(sections, dict) and sections.get('market_size'):
                has_market_section = True
            qi = (dp.structured_data or {}).get('quality_indicators', {})
            if isinstance(qi, dict) and isinstance(qi.get('section_coverage'), (int, float)):
                section_coverage = max(section_coverage, float(qi['section_coverage']))

        if has_market_section:
            signals.append('Pitch deck includes market sizing section')
        if section_coverage:
            signals.append(f"Pitch deck section coverage: {section_coverage:.2f}")

        wp_quality = 0.0
        for dp in whitepapers:
            quality = (dp.structured_data or {}).get('writing_quality', {})
            if not isinstance(quality, dict):
                continue

            score_parts: List[float] = []
            for key in ['reading_ease', 'has_abstract', 'has_references', 'academic_language', 'has_figures']:
                value = quality.get(key)
                if isinstance(value, (int, float)):
                    score_parts.append(float(value))

            if score_parts:
                wp_quality = max(wp_quality, sum(score_parts) / len(score_parts))

        if wp_quality:
            signals.append(f"Whitepaper writing quality: {wp_quality:.2f}")

        site_info_completeness = 0.0
        for dp in websites:
            company_info = (dp.structured_data or {}).get('company_information', {})
            if isinstance(company_info, dict):
                present = sum(1 for v in company_info.values() if v)
                total = max(1, len(company_info))
                site_info_completeness = max(site_info_completeness, present / total)

        if site_info_completeness:
            signals.append(f"Website company info completeness: {site_info_completeness:.2f}")

        score = 0.0
        score += 0.45 if has_market_section else 0.15
        score += min(section_coverage, 1.0) * 0.25
        score += min(site_info_completeness, 1.0) * 0.2
        score += min(wp_quality, 1.0) * 0.1

        score = max(0.0, min(1.0, score))

        return {
            'score': int(round(score * 100)),
            'signals': signals,
            'summary': 'Heuristic market signal score derived from pitch deck/website/whitepaper coverage.'
        }

    def _compute_competition(
        self,
        *,
        pitch_decks: List[DQDADataPoint],
        websites: List[DQDADataPoint],
    ) -> Dict[str, Any]:
        signals: List[str] = []
        has_competitive_section = False

        for dp in pitch_decks:
            sections = (dp.structured_data or {}).get('sections', {})
            if isinstance(sections, dict) and sections.get('competitive_advantage'):
                has_competitive_section = True

        if has_competitive_section:
            signals.append('Pitch deck discusses competitive advantage')

        pages_crawled = 0
        for dp in websites:
            crawled_pages = (dp.structured_data or {}).get('crawled_pages', {})
            if isinstance(crawled_pages, dict):
                pages_crawled = max(pages_crawled, len(crawled_pages))

        if pages_crawled:
            signals.append(f"Website pages crawled: {pages_crawled}")

        score = 0.6 if has_competitive_section else 0.3
        score += min(pages_crawled / 10, 1.0) * 0.4
        score = max(0.0, min(1.0, score))

        return {
            'score': int(round(score * 100)),
            'signals': signals,
            'summary': 'Competition analysis is inferred from presence of competitive sections and website coverage.'
        }

    def _compute_token_utility(self, tokens: List[DQDADataPoint]) -> Dict[str, Any]:
        if not tokens:
            return {
                'score': 0,
                'signals': ['No tokenomics data available'],
                'summary': 'Token utility score could not be computed due to missing token data.'
            }

        quality_scores: List[float] = []
        for dp in tokens:
            qs = (dp.structured_data or {}).get('quality_score')
            if isinstance(qs, (int, float)):
                quality_scores.append(float(qs))
            else:
                quality_scores.append(float(dp.confidence_score))

        avg = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        avg = max(0.0, min(1.0, avg))

        return {
            'score': int(round(avg * 100)),
            'signals': ['Derived from tokenomics collector quality/confidence'],
            'summary': 'Heuristic token utility proxy based on available tokenomics data quality.'
        }

    def _identify_weaknesses(
        self,
        *,
        founder_score: int,
        market_analysis: Dict[str, Any],
        competition: Dict[str, Any],
        token_utility: Dict[str, Any],
        collected: Dict[str, List[DQDADataPoint]],
    ) -> List[str]:
        weaknesses: List[str] = []

        if founder_score < 40:
            weaknesses.append('Low founder/team signal score')

        if int(market_analysis.get('score', 0)) < 40:
            weaknesses.append('Weak market evidence (limited market sizing / positioning signals)')

        if int(competition.get('score', 0)) < 40:
            weaknesses.append('Limited competitive differentiation evidence')

        if int(token_utility.get('score', 0)) < 40:
            weaknesses.append('Token utility/quality signal is weak or missing')

        if not collected.get('pitch_deck'):
            weaknesses.append('No pitch deck data collected')
        if not collected.get('whitepaper'):
            weaknesses.append('No whitepaper data collected')
        if not collected.get('website'):
            weaknesses.append('No website crawl data collected')
        if not collected.get('tokenomics'):
            weaknesses.append('No tokenomics data collected')
        if not collected.get('founders'):
            weaknesses.append('No founder background data collected')

        return weaknesses

    def _compute_investor_fit(
        self,
        *,
        founder_score: int,
        market_score: float,
        competition_score: float,
        token_score: float,
        weaknesses: List[str],
    ) -> Dict[str, Any]:
        normalized = (
            founder_score / 100.0 * 0.35
            + market_score / 100.0 * 0.3
            + competition_score / 100.0 * 0.15
            + token_score / 100.0 * 0.2
        )

        penalty = min(len(weaknesses) * 0.02, 0.2)
        normalized = max(0.0, min(1.0, normalized - penalty))

        score = int(round(normalized * 100))

        if score >= 75:
            rating = 'strong'
        elif score >= 55:
            rating = 'moderate'
        else:
            rating = 'weak'

        return {
            'score': score,
            'rating': rating,
            'rationale': 'Weighted composite of founder/market/competition/token signals with a small penalty for flagged weaknesses.',
        }
