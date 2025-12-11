"""Regression tests for DQDA end-to-end orchestration + reporting exports."""

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

# Add the agent module to the path
import sys

sys.path.append('/home/engine/project')

from agent.dqda.dqda_agent import DQDAAgent
from agent.dqda.reporting import DQDAReportExporter
from agent.dqda.data_collectors.base_collector import DQDADataPoint, DataSource


class _MockCollector:
    def __init__(self, data_points):
        self._data_points = data_points
        self.calls = []

    async def collect_data(self, startup_name: str, keywords, max_results: int = 10, **kwargs):
        self.calls.append(
            {
                'startup_name': startup_name,
                'keywords': keywords,
                'max_results': max_results,
                'kwargs': kwargs,
            }
        )
        return self._data_points[:max_results]


class TestDQDAAgentEndToEnd(unittest.IsolatedAsyncioTestCase):
    async def test_end_to_end_report_contains_core_outputs_and_exports(self):
        startup_name = 'Acme Protocol'
        keywords = ['blockchain', 'defi']

        pitch_dp = DQDADataPoint(
            startup_name=startup_name,
            source_type=DataSource.PITCH_DECK,
            source_url='https://example.com/deck.pdf',
            raw_content='market size ... competitive advantage ...',
            structured_data={
                'sections': {
                    'market_size': 'TAM is $1B',
                    'competitive_advantage': 'moat',
                },
                'quality_indicators': {'section_coverage': 0.8},
            },
            confidence_score=0.85,
        )

        wp_dp = DQDADataPoint(
            startup_name=startup_name,
            source_type=DataSource.WHITEPAPER,
            source_url='https://example.com/whitepaper.pdf',
            raw_content='technical details ...',
            structured_data={
                'writing_quality': {'overall_quality': 0.7},
                'key_insights': ['insight 1'],
            },
            confidence_score=0.8,
        )

        web_dp = DQDADataPoint(
            startup_name=startup_name,
            source_type=DataSource.WEBSITE,
            source_url='https://acme.example.com',
            raw_content='about ...',
            structured_data={
                'company_information': {
                    'industry': 'DeFi',
                    'description': 'On-chain credit',
                    'location': 'Remote',
                },
                'crawled_pages': {
                    'https://acme.example.com/about': {'title': 'About', 'content_length': 500, 'priority_page': 'about'}
                },
            },
            confidence_score=0.75,
        )

        token_dp = DQDADataPoint(
            startup_name=startup_name,
            source_type=DataSource.TOKENOMICS,
            source_url='https://etherscan.io/token/0xabc',
            raw_content=None,
            structured_data={
                'quality_score': 0.9,
                'metadata': {'symbol': 'ACME'},
                'market_data': {'market_cap': 123456789},
            },
            confidence_score=0.9,
        )

        founder_dp = DQDADataPoint(
            startup_name=startup_name,
            source_type=DataSource.FOUNDER_PROFILE,
            source_url='https://linkedin.com/in/founder',
            raw_content=None,
            structured_data={
                'founder_name': 'Jane Doe',
                'overall_assessment': {
                    'overall_score': 0.76,
                    'strengths': ['Strong educational background'],
                    'weaknesses': [],
                    'recommendation': 'positive',
                },
            },
            confidence_score=0.8,
        )

        agent = DQDAAgent(
            pitch_deck_parser=_MockCollector([pitch_dp]),
            whitepaper_processor=_MockCollector([wp_dp]),
            website_crawler=_MockCollector([web_dp]),
            tokenomics_collector=_MockCollector([token_dp]),
            founder_background_collector=_MockCollector([founder_dp]),
        )

        report = await agent.run_full_pipeline(
            startup_name=startup_name,
            keywords=keywords,
            max_results=2,
            website_urls=['https://acme.example.com'],
            tokenomics_use_test_data=True,
        )

        for key in [
            'founder_score',
            'market_analysis',
            'competition',
            'token_utility',
            'weaknesses',
            'investor_fit',
        ]:
            self.assertIn(key, report)

        self.assertIsInstance(report['founder_score'], int)
        self.assertIsInstance(report['weaknesses'], list)

        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = DQDAReportExporter(output_dir=Path(tmpdir))

            json_path = exporter.export(report, format='json', filename='dqda_test')
            csv_path = exporter.export(report, format='csv', filename='dqda_test')
            xlsx_path = exporter.export(report, format='xlsx', filename='dqda_test')

            # JSON: ensure all core outputs are present
            with open(json_path, 'r', encoding='utf-8') as f:
                exported_json = json.load(f)
            for key in [
                'founder_score',
                'market_analysis',
                'competition',
                'token_utility',
                'weaknesses',
                'investor_fit',
            ]:
                self.assertIn(key, exported_json)

            # CSV: ensure serialized columns exist
            df = pd.read_csv(csv_path)
            for col in [
                'founder_score',
                'market_analysis',
                'competition',
                'token_utility',
                'weaknesses',
                'investor_fit',
            ]:
                self.assertIn(col, df.columns)

            # Excel: ensure dashboard sheet exists + columns
            dashboard_df = pd.read_excel(xlsx_path, sheet_name='Dashboard')
            for col in [
                'founder_score',
                'market_analysis',
                'competition',
                'token_utility',
                'weaknesses',
                'investor_fit',
            ]:
                self.assertIn(col, dashboard_df.columns)


if __name__ == '__main__':
    unittest.main(verbosity=2)
