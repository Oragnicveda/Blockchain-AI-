#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from agent import StartupResearchAgent
from agent.utils.logger import setup_logger

logger = setup_logger('main')


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='AI Agent for researching blockchain, crypto, and Web3 startups with funding'
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
        help='Maximum number of results per category (default: 50)'
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
        logger.info("Initializing AI Startup Research Agent...")
        agent = StartupResearchAgent()
        
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
