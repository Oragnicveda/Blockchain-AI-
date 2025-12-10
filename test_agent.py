#!/usr/bin/env python3
import sys
from agent import StartupResearchAgent


def test_basic_functionality():
    print("Testing AI Startup Research Agent...\n")
    
    print("1. Initializing agent...")
    agent = StartupResearchAgent()
    print("   ✓ Agent initialized successfully\n")
    
    print("2. Testing data collection...")
    results = agent.research_startups(
        categories=['blockchain'],
        max_results=5,
        include_news=False
    )
    print(f"   ✓ Collected {len(results)} startups\n")
    
    if results:
        print("3. Sample startup data:")
        startup = results[0]
        print(f"   Name: {startup.get('name')}")
        print(f"   Category: {startup.get('category')}")
        print(f"   Funding: {startup.get('funding_amount')}")
        print(f"   Valuation: {startup.get('valuation')}")
        print(f"   Investors: {', '.join(startup.get('investors', [])[:3])}")
        print()
    
    print("4. Testing summary generation...")
    agent.print_summary(results)
    
    print("5. Testing export functionality...")
    try:
        json_path = agent.export_results(results, format='json', filename='test_export')
        print(f"   ✓ JSON export successful: {json_path}\n")
        
        csv_path = agent.export_results(results, format='csv', filename='test_export')
        print(f"   ✓ CSV export successful: {csv_path}\n")
    except Exception as e:
        print(f"   ✗ Export failed: {str(e)}\n")
        return False
    
    print("="*60)
    print("All tests passed! ✓")
    print("="*60)
    return True


if __name__ == '__main__':
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
