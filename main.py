#!/usr/bin/env python3
import argparse
import asyncio
import sys

from agent import StartupResearchAgent
from agent.utils.logger import setup_logger

logger = setup_logger('main')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='AI Agent for researching blockchain, crypto, and Web3 startups with funding'
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--seed-funding',
        action='store_true',
        help='Research seed funding from crypto startups with investor metrics'
    )
    mode_group.add_argument(
        '--dqda',
        action='store_true',
        help='Run the DQDA due diligence scoring pipeline for a single startup'
    )

    parser.add_argument(
        '--startup-name',
        type=str,
        default=None,
        help='Startup name (required for --dqda)'
    )

    parser.add_argument(
        '--keywords',
        nargs='+',
        default=None,
        help='Search/analysis keywords (used for --dqda; defaults to categories)'
    )

    parser.add_argument(
        '--website-url',
        nargs='*',
        default=None,
        help='Base website URL(s) to crawl (used for --dqda)'
    )

    parser.add_argument(
        '--tokenomics-test-data',
        action='store_true',
        help='Use built-in tokenomics test data (helps avoid external API calls)'
    )

    parser.add_argument(
        '--categories',
        nargs='+',
        default=['blockchain', 'crypto', 'web3', 'ai', 'defi', 'nft'],
        help='Categories to research (e.g., blockchain crypto web3 ai)'
    )

    parser.add_argument(
        '--max-results',
        type=int,
        default=50,
        help='Maximum results (per category for startup mode; per collector for DQDA)'
    )

    parser.add_argument(
        '--output-format',
        choices=['json', 'csv', 'xlsx', 'all'],
        default='all',
        help='Output format (default: all)'
    )

    parser.add_argument(
        '--output-filename',
        type=str,
        default=None,
        help='Custom output filename (without extension)'
    )

    parser.add_argument(
        '--no-news',
        action='store_true',
        help='Skip news aggregation'
    )

    parser.add_argument(
        '--summary-only',
        action='store_true',
        help='Only print summary without exporting data'
    )

    return parser.parse_args()


def main():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   AI Startup Research Agent                                  ║
    ║   Blockchain | Crypto | Web3 | AI                            ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    args = parse_arguments()
    
    try:
        if args.dqda:
            if not args.startup_name:
                logger.error("--startup-name is required when using --dqda")
                return 2

            from agent.dqda.dqda_agent import DQDAAgent
            from agent.dqda.reporting import DQDAReportExporter

            keywords = args.keywords or args.categories
            website_urls = args.website_url or []

            logger.info("Initializing DQDA Agent...")
            dqda_agent = DQDAAgent()

            report = asyncio.run(
                dqda_agent.run_full_pipeline(
                    startup_name=args.startup_name,
                    keywords=keywords,
                    max_results=args.max_results,
                    website_urls=website_urls,
                    tokenomics_use_test_data=args.tokenomics_test_data,
                )
            )

            dqda_agent.print_summary(report)

            if not args.summary_only:
                exporter = DQDAReportExporter()
                formats = ['json', 'csv', 'xlsx'] if args.output_format == 'all' else [args.output_format]
                for fmt in formats:
                    output_path = exporter.export(report, format=fmt, filename=args.output_filename)
                    print(f"✓ Exported {fmt.upper()}: {output_path}")

            print("\n✓ DQDA pipeline complete!")
            return 0

        logger.info("Initializing AI Startup Research Agent...")
        agent = StartupResearchAgent()

        # Handle seed funding research mode
        if args.seed_funding:
            logger.info("Seed Funding Research Mode enabled")
            seed_funding_data, investor_report = agent.research_seed_funding(
                max_results=args.max_results,
                generate_investor_report=True
            )

            if not seed_funding_data:
                logger.warning("No seed funding data found")
                return 1

            agent.print_seed_funding_summary(investor_report)

            if not args.summary_only:
                formats = ['json', 'csv', 'xlsx'] if args.output_format == 'all' else [args.output_format]

                for fmt in formats:
                    output_path = agent.export_seed_funding_results(
                        seed_funding_data,
                        investor_report=investor_report,
                        format=fmt,
                        filename=args.output_filename
                    )
                    print(f"✓ Exported {fmt.upper()}: {output_path}")

            print(f"\n✓ Seed funding research complete! Collected data on {len(seed_funding_data)} funding rounds")
            return 0
        
        # Regular startup research mode
        logger.info(f"Starting research for categories: {', '.join(args.categories)}")
        
        startups = agent.research_startups(
            categories=args.categories,
            max_results=args.max_results,
            include_news=not args.no_news
        )
        
        if not startups:
            logger.warning("No startups found matching the criteria")
            return 1
        
        agent.print_summary(startups)
        
        if not args.summary_only:
            formats = ['json', 'csv', 'xlsx'] if args.output_format == 'all' else [args.output_format]
            
            for fmt in formats:
                output_path = agent.export_results(
                    startups,
                    format=fmt,
                    filename=args.output_filename
                )
                print(f"✓ Exported {fmt.upper()}: {output_path}")
        
        print(f"\n✓ Research complete! Collected data on {len(startups)} startups")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Research interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Error during research: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
