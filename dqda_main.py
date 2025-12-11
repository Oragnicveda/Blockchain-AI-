import argparse
import asyncio
import sys
import json
import os
from agent.dqda import DealQualificationAgent, DealInput, DQDAConfig
from agent.dqda.data_collectors import (
    PitchDeckParser,
    WhitepaperProcessor,
    WebsiteCrawler,
    TokenomicsCollector,
    FounderBackgroundCollector
)
from agent.utils.logger import setup_logger

logger = setup_logger("dqda_cli")

def parse_args():
    parser = argparse.ArgumentParser(description="Deal Qualification Agent (DQDA) CLI")
    parser.add_argument("startup_name", help="Name of the startup to analyze")
    parser.add_argument("--pitch-deck", help="Path or URL to pitch deck PDF")
    parser.add_argument("--whitepaper", help="Path or URL to whitepaper PDF/text")
    parser.add_argument("--website", help="Website URL")
    parser.add_argument("--token", help="Token symbol (e.g. BTC, ETH)")
    parser.add_argument("--keywords", nargs="+", help="Additional keywords for search")
    parser.add_argument("--output-format", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--output-file", help="Path to save output")
    
    return parser.parse_args()

async def main():
    args = parse_args()
    
    logger.info(f"Initializing DQDA for {args.startup_name}...")
    
    # Initialize Agent
    config = DQDAConfig()
    agent = DealQualificationAgent(config)
    
    # Wire up collectors
    # Registering all collectors for now.
    # In the future we might want to selectively register based on input, 
    # but for search capabilities we want them all.
    
    agent.register_collector(PitchDeckParser())
    agent.register_collector(WhitepaperProcessor())
    agent.register_collector(WebsiteCrawler())
    agent.register_collector(TokenomicsCollector())
    agent.register_collector(FounderBackgroundCollector())
    
    # Create input
    deal_input = DealInput(
        startup_name=args.startup_name,
        pitch_deck_path=args.pitch_deck,
        website_url=args.website,
        whitepaper_path=args.whitepaper,
        token_symbol=args.token,
        additional_keywords=args.keywords or []
    )
    
    print(f"\n--- DQDA Scaffolding Analysis: {args.startup_name} ---\n")
    print("Collecting data from registered sources...")
    
    # Run Agent
    try:
        assessment = await agent.run(deal_input)
    except Exception as e:
        logger.error(f"Error during agent execution: {e}")
        print(f"Error: {e}")
        return

    # Output
    if args.output_format == "json":
        output = json.dumps(assessment.to_dict(), indent=2)
        print(output)
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
    else:
        # Text summary
        print(f"\n=== Deal Assessment: {assessment.startup_name} ===")
        print(f"Overall Score: {assessment.overall_score:.2f}/10")
        print(f"Confidence: {assessment.confidence_score:.2f}")
        print(f"Timestamp: {assessment.assessment_timestamp}")
        print("\nCategory Scores:")
        for cat, score in assessment.category_scores.items():
            print(f"  - {cat.capitalize()}: {score:.2f}")
            
        print("\nFlags:")
        if assessment.flags:
            for flag in assessment.flags:
                print(f"  [!] {flag}")
        else:
            print("  None")
            
        print(f"\nData Points Collected: {len(assessment.data_points)}")
        for dp in assessment.data_points:
            source = dp.source_type.value if hasattr(dp.source_type, 'value') else str(dp.source_type)
            print(f"  - [{source}] Confidence: {dp.confidence_score:.2f}")
            
        if args.output_file:
             with open(args.output_file, 'w') as f:
                f.write(f"Deal Assessment: {assessment.startup_name}\n")
                f.write(f"Score: {assessment.overall_score}\n")

if __name__ == "__main__":
    asyncio.run(main())
