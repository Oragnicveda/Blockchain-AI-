#!/usr/bin/env python3
"""Test script for text export functionality"""
import sys
from agent import StartupResearchAgent


def test_text_export():
    print("Testing Text Export Functionality...\n")
    
    print("1. Initializing agent...")
    agent = StartupResearchAgent()
    print("   ✓ Agent initialized successfully\n")
    
    print("2. Testing regular startup research with text export...")
    results = agent.research_startups(
        categories=['blockchain'],
        max_results=3,
        include_news=False
    )
    print(f"   ✓ Collected {len(results)} startups\n")
    
    if results:
        print("3. Exporting to text format...")
        try:
            txt_path = agent.export_results(results, format='txt', filename='test_text_export')
            print(f"   ✓ Text export successful: {txt_path}\n")
            
            # Display a sample of the text file
            print("4. Sample of text export (first 30 lines):")
            print("-" * 80)
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:30]
                for line in lines:
                    print(line.rstrip())
            print("-" * 80)
            print()
        except Exception as e:
            print(f"   ✗ Text export failed: {str(e)}\n")
            import traceback
            traceback.print_exc()
            return False
    
    print("5. Testing seed funding research with text export...")
    try:
        seed_funding_data, investor_report = agent.research_seed_funding(
            max_results=3,
            generate_investor_report=True
        )
        
        if seed_funding_data:
            print(f"   ✓ Collected {len(seed_funding_data)} seed funding rounds\n")
            
            print("6. Exporting seed funding to text format...")
            txt_path = agent.export_seed_funding_results(
                seed_funding_data,
                investor_report=investor_report,
                format='txt',
                filename='test_seed_funding_text_export'
            )
            print(f"   ✓ Seed funding text export successful: {txt_path}\n")
            
            # Display a sample of the seed funding text file
            print("7. Sample of seed funding text export (first 50 lines):")
            print("-" * 80)
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:50]
                for line in lines:
                    print(line.rstrip())
            print("-" * 80)
            print()
    except Exception as e:
        print(f"   ✗ Seed funding text export failed: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 80)
    print("All text export tests passed! ✓")
    print("=" * 80)
    return True


if __name__ == '__main__':
    try:
        success = test_text_export()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
