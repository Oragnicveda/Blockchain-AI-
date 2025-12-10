#!/usr/bin/env python3
import sys
from agent import StartupResearchAgent


def test_seed_funding_functionality():
    print("Testing Seed Funding Research Feature...\n")
    
    print("1. Initializing agent...")
    agent = StartupResearchAgent()
    print("   ✓ Agent initialized successfully\n")
    
    print("2. Testing seed funding data collection...")
    seed_funding_data, investor_report = agent.research_seed_funding(
        max_results=10,
        generate_investor_report=True
    )
    print(f"   ✓ Collected {len(seed_funding_data)} seed funding rounds\n")
    
    if seed_funding_data:
        print("3. Verifying seed funding data structure:")
        startup = seed_funding_data[0]
        print(f"   Startup: {startup.get('startup_name')}")
        print(f"   Funding Amount: {startup.get('funding_amount')}")
        print(f"   Source Site: {startup.get('source_site')}")
        print(f"   Investors: {startup.get('investors')}")
        print(f"   Lead Investor: {startup.get('lead_investor')}")
        print()
    
    print("4. Testing investor report generation...")
    if investor_report:
        print("   ✓ Investor report generated successfully")
        summary = investor_report.get('summary', {})
        print(f"   Total Seed Funding: {summary.get('total_seed_funding_raised')}")
        print(f"   Total Seed Rounds: {summary.get('total_seed_rounds_tracked')}")
        print(f"   Unique Investors: {summary.get('unique_investors_identified')}")
        print()
    
    print("5. Verifying source site tracking...")
    source_analysis = investor_report.get('source_analysis', {})
    if source_analysis:
        print("   Data sources tracked:")
        for site, data in source_analysis.items():
            print(f"   - {site}: {data['funding_rounds']} rounds, ${data['total_funding']:,.0f} total")
    print()
    
    print("6. Testing export functionality...")
    try:
        json_path = agent.export_seed_funding_results(
            seed_funding_data,
            investor_report=investor_report,
            format='json',
            filename='test_seed_funding'
        )
        print(f"   ✓ JSON export successful: {json_path}\n")
        
        xlsx_path = agent.export_seed_funding_results(
            seed_funding_data,
            investor_report=investor_report,
            format='xlsx',
            filename='test_seed_funding'
        )
        print(f"   ✓ Excel export successful: {xlsx_path}\n")
    except Exception as e:
        print(f"   ✗ Export failed: {str(e)}\n")
        return False
    
    print("7. Testing summary print...")
    agent.print_seed_funding_summary(investor_report)
    
    print("="*60)
    print("All seed funding tests passed! ✓")
    print("="*60)
    return True


if __name__ == '__main__':
    try:
        success = test_seed_funding_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
