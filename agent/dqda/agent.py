import asyncio
from typing import List, Optional
from agent.utils.logger import setup_logger
from agent.dqda.config import DQDAConfig
from agent.dqda.models import DealInput, DealAssessment
from agent.dqda.data_collectors.base_collector import BaseCollector, DQDADataPoint

class DealQualificationAgent:
    def __init__(self, config: Optional[DQDAConfig] = None):
        self.logger = setup_logger(__name__)
        self.config = config or DQDAConfig()
        self.collectors: List[BaseCollector] = []
        
        # Ensure output directory exists
        self.config.ensure_output_dir()
        
    def register_collector(self, collector: BaseCollector):
        """Register a data collector."""
        self.collectors.append(collector)
        self.logger.info(f"Registered collector: {collector.__class__.__name__}")

    async def run(self, deal_input: DealInput) -> DealAssessment:
        self.logger.info(f"Starting analysis for: {deal_input.startup_name}")
        
        # Collect data
        tasks = []
        for collector in self.collectors:
            # Prepare keywords
            keywords = [deal_input.startup_name] + deal_input.additional_keywords
            
            # Pass relevant info to collectors
            # Some collectors might need specific URLs (pitch deck, website)
            # BaseCollector.collect_data takes **kwargs.
            
            kwargs = {}
            if deal_input.pitch_deck_path:
                kwargs['pitch_deck_path'] = deal_input.pitch_deck_path
            if deal_input.website_url:
                kwargs['website_url'] = deal_input.website_url
                kwargs['base_urls'] = [deal_input.website_url]
            if deal_input.whitepaper_path:
                kwargs['whitepaper_path'] = deal_input.whitepaper_path
            if deal_input.token_symbol:
                kwargs['token_symbol'] = deal_input.token_symbol
                
            tasks.append(collector.collect_data(
                startup_name=deal_input.startup_name,
                keywords=keywords,
                **kwargs
            ))
            
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_data_points: List[DQDADataPoint] = []
        for result in results_lists:
            if isinstance(result, list):
                all_data_points.extend(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Collector failed: {result}")
        
        # Analyze/Score (Placeholder logic for now as requested by "scaffold")
        assessment = self._calculate_assessment(deal_input.startup_name, all_data_points)
        
        self.logger.info(f"Analysis complete for {deal_input.startup_name}. Score: {assessment.overall_score}")
        return assessment

    def _calculate_assessment(self, startup_name: str, data_points: List[DQDADataPoint]) -> DealAssessment:
        # Simple placeholder scoring logic
        # In a real implementation, this would use the config weights and analyze the structured data
        
        total_score = 0.0
        # Just a dummy calculation based on confidence scores and quantity
        if not data_points:
             return DealAssessment(
                startup_name=startup_name,
                overall_score=0.0,
                confidence_score=0.0
            )

        avg_confidence = sum(dp.confidence_score for dp in data_points) / len(data_points)
        
        # Mock category scoring
        category_scores = {}
        for cat, weight in self.config.SCORING_WEIGHTS.items():
            # Normalized score contribution (mock)
            # Assuming we found some data relevant to the category
            # For now just giving a fixed dummy score
            score_val = 7.5 # 7.5/10
            category_scores[cat] = score_val
            total_score += score_val * weight
            
        return DealAssessment(
            startup_name=startup_name,
            overall_score=min(total_score, 10.0), # Cap at 10
            confidence_score=avg_confidence,
            data_points=data_points,
            category_scores=category_scores,
            flags=["Scaffold Mode"]
        )
