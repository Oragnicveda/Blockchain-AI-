# Seed Funding Research Guide

## Overview

This guide explains how to use the new Seed Funding Research feature that gathers the latest seed funding from crypto startups and provides investor-focused metrics with site names.

## Quick Start

### Basic Command
```bash
python main.py --seed-funding
```

### With Options
```bash
# Collect 20 seed funding rounds and export to all formats
python main.py --seed-funding --max-results 20 --output-format all

# Only display summary without exporting
python main.py --seed-funding --summary-only

# Export to specific format
python main.py --seed-funding --output-format json --output-filename crypto-seed-rounds
```

## Features

### 1. Multi-Source Data Collection
The seed funding collector gathers data from multiple sources:
- **Crunchbase**: Early-stage startup funding data
- **PitchBook**: Venture funding database
- **TechCrunch**: News and announcements
- **CB Insights**: Market intelligence platform

Each data source is tracked, allowing investors to see where information originates.

### 2. Investor-Focused Metrics

The report includes:
- **Total Seed Funding Raised**: Sum of all seed round amounts
- **Average Seed Round Size**: Mean funding per round
- **Total Seed Rounds Tracked**: Number of funding rounds analyzed
- **Unique Investors Identified**: Total number of unique investors
- **Average Investors per Round**: Mean investor count per funding round

### 3. Most Active Investors
Identifies investors who participate most frequently in seed rounds:
```
Most Active Investors (Top 10):
1. Animoca Brands - 2 participations
2. Sequoia Capital - 2 participations
3. Pantera Capital - 2 participations
...
```

### 4. Lead Investor Summary
Shows the primary investor for each seed round with:
- Number of investments (as lead investor)
- Total amount invested
- Average investment per round

### 5. Funding Data Sources (Site Names)
Displays aggregated metrics by source:
```
Funding Data Sources (Site Names):
- Crunchbase:
    Funding Rounds: 3
    Total Funding: $83,000,000
    Unique Investors: 9
- PitchBook:
    Funding Rounds: 2
    Total Funding: $100,000,000
    Unique Investors: 6
...
```

### 6. Industry & Geographic Breakdown
- **Industry Breakdown**: Shows distribution across sectors (Blockchain, DeFi, NFT, etc.)
- **Geographic Distribution**: Shows startup locations by country/city

## Output Formats

### 1. JSON Export
Complete structured data including:
- All seed funding rounds with full details
- Investor report with metrics
- Source tracking information

```bash
python main.py --seed-funding --output-format json
```

### 2. CSV Export
Tab-separated values with all seed funding columns:
- startup_name, funding_amount, funding_round
- investors, source_site, announcement_date
- headquarters, industry, lead_investor
- And more...

```bash
python main.py --seed-funding --output-format csv
```

### 3. Excel Export (Recommended for Investors)
Multiple sheets for comprehensive analysis:
- **Seed Funding Rounds**: All funding rounds with details
- **Summary**: Key metrics and statistics
- **Most Active Investors**: Top investor participation data
- **Source Analysis**: Metrics by data source/site name

```bash
python main.py --seed-funding --output-format xlsx
```

## Data Fields

Each seed funding round contains:
- **startup_name**: Company name
- **funding_amount**: Round size (e.g., "$20M")
- **funding_round**: Round type (e.g., "Seed", "Seed Extension")
- **announcement_date**: When funding was announced
- **investors**: List of participating investors
- **num_investors**: Count of investors
- **source_site**: Where data was sourced (Crunchbase, PitchBook, etc.)
- **source_url**: Direct link to the source
- **description**: Company description
- **headquarters**: HQ location
- **industry**: Industry category
- **investor_type**: Type of investors (VC Firms, Angel Investors, etc.)
- **average_investment_per_investor**: Average per investor
- **lead_investor**: Primary investor for round
- **funding_timeline**: Stage (e.g., "Early Stage")

## Example Usage Scenarios

### Scenario 1: Analyzing Investor Activity
```bash
python main.py --seed-funding --output-format xlsx
```
Open the Excel file and review:
- "Most Active Investors" sheet to identify active investors
- "Source Analysis" sheet to see where they're most visible
- "Summary" sheet for overall metrics

### Scenario 2: Tracking by Data Source
Want to understand which investors are found on which platforms?
- Export to JSON
- Filter by `source_site` field
- Analyze investor presence across sources

### Scenario 3: Industry-Specific Analysis
Look at the "Industry Breakdown" in the summary to understand:
- Which blockchain sectors are getting seed funding
- Geographic concentration of innovation
- Lead investor preferences by industry

## Testing

Run the seed funding test:
```bash
python test_seed_funding.py
```

This will:
1. Initialize the agent
2. Collect seed funding data
3. Verify data structure and source tracking
4. Generate investor report
5. Test all export formats
6. Display summary

## Integration with Existing Features

The seed funding feature works alongside existing startup research:
```bash
# Regular startup research (unchanged)
python main.py --categories blockchain crypto --max-results 50

# Seed funding research (new)
python main.py --seed-funding --max-results 50

# Both features use same export mechanisms
```

## API Structure

### Using in Python Code

```python
from agent import StartupResearchAgent

agent = StartupResearchAgent()

# Research seed funding
seed_funding_data, investor_report = agent.research_seed_funding(
    max_results=20,
    generate_investor_report=True
)

# Export results
agent.export_seed_funding_results(
    seed_funding_data,
    investor_report=investor_report,
    format='xlsx',
    filename='my_seed_analysis'
)

# Print summary
agent.print_seed_funding_summary(investor_report)
```

## Key Metrics Explained

### Total Seed Funding Raised
Sum of all seed round sizes in the dataset. Indicates overall capital flowing into early-stage crypto startups.

### Average Seed Round Size
Mean funding per seed round. Higher averages indicate larger typical investments.

### Unique Investors Identified
Total number of distinct investors across all rounds. Indicates market diversity.

### Average Investors per Round
Mean number of investors per round. Shows typical syndication patterns.

## Source Credibility

Each funding round is tracked with its source:
- Data from multiple sources reduces bias
- Source URLs are included for verification
- Consistent appearance across sources adds credibility
- CB Insights and Crunchbase are industry standards

## Best Practices

1. **Cross-reference sources**: Check if investors appear across multiple platforms
2. **Review dates**: Ensure funding announcements are recent (see announcement_date)
3. **Verify URLs**: Click through to official sources for confirmation
4. **Industry analysis**: Filter by industry for sector-specific insights
5. **Geographic focus**: Look for regional concentration patterns

## Troubleshooting

### No data returned
- Check internet connection
- Verify APIs are accessible (simulated data is used as fallback)
- Try with smaller `--max-results` first

### Export errors
- Ensure `/output` directory exists
- Check write permissions
- Try CSV format as fallback

### Summary not displaying
- Verify `investor_report` is not None
- Check log files for errors

## Future Enhancements

Potential improvements:
- Real API integration with Crunchbase and PitchBook
- Real-time data updates
- Investor network analysis
- Deal flow prediction
- Performance tracking post-funding
