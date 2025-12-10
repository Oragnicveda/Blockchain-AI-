# Usage Examples

## Basic Examples

### 1. Research All Categories

```bash
python main.py
```

This will research all default categories (blockchain, crypto, web3, ai, defi, nft) and export results in all formats.

### 2. Research Specific Categories

```bash
python main.py --categories blockchain crypto
```

Research only blockchain and crypto startups.

### 3. Limit Results

```bash
python main.py --max-results 20
```

Limit to 20 results per category.

### 4. Custom Output Format

```bash
# JSON only
python main.py --output-format json

# CSV only
python main.py --output-format csv

# Excel only
python main.py --output-format xlsx
```

### 5. Custom Filename

```bash
python main.py --output-filename my_research_2024
```

### 6. Summary Only (No Export)

```bash
python main.py --summary-only
```

Just print the summary statistics without exporting files.

### 7. Skip News Aggregation

```bash
python main.py --no-news
```

## Advanced Examples

### Research Web3 and AI with Limited Results

```bash
python main.py --categories web3 ai --max-results 30 --output-format xlsx
```

### Quick Summary of Blockchain Startups

```bash
python main.py --categories blockchain --summary-only --no-news
```

## Programmatic Usage

### Basic Usage

```python
from agent import StartupResearchAgent

# Initialize agent
agent = StartupResearchAgent()

# Research startups
results = agent.research_startups(
    categories=['blockchain', 'crypto'],
    max_results=50
)

# Print summary
agent.print_summary(results)

# Export to JSON
agent.export_results(results, format='json', filename='my_results')
```

### Advanced Usage with Custom Processing

```python
from agent import StartupResearchAgent

agent = StartupResearchAgent()

# Research all categories
all_startups = agent.research_startups()

# Filter high-value startups
high_value = [
    s for s in all_startups 
    if s.get('valuation') and 'B' in s['valuation']
]

# Export filtered results
agent.export_results(high_value, format='xlsx', filename='unicorns')

# Generate and display summary
summary = agent.generate_summary(high_value)
print(f"Found {summary['total_startups']} unicorn startups")
```

### Batch Processing Multiple Searches

```python
from agent import StartupResearchAgent

agent = StartupResearchAgent()

categories_groups = [
    ['blockchain', 'crypto'],
    ['web3', 'nft'],
    ['ai', 'defi']
]

for group in categories_groups:
    results = agent.research_startups(categories=group, max_results=25)
    filename = f"{'_'.join(group)}_startups"
    agent.export_results(results, format='json', filename=filename)
    print(f"Exported {len(results)} startups for {group}")
```

### Custom Data Processing

```python
from agent import StartupResearchAgent
from agent.processors import DataParser

agent = StartupResearchAgent()
results = agent.research_startups()

# Calculate total funding by category
funding_by_category = {}
parser = DataParser()

for startup in results:
    category = startup.get('category', 'Unknown')
    funding_str = startup.get('funding_amount', '$0')
    funding_value = parser.parse_funding_amount(funding_str) or 0
    
    if category not in funding_by_category:
        funding_by_category[category] = 0
    funding_by_category[category] += funding_value

# Print results
for category, total in sorted(funding_by_category.items(), key=lambda x: x[1], reverse=True):
    print(f"{category}: ${total:,.0f}")
```

## Output Examples

### JSON Output

```json
[
  {
    "name": "Chainalysis",
    "description": "Blockchain data platform providing investigation and compliance tools",
    "category": "Blockchain",
    "funding_amount": "$366M",
    "funding_round": "Series F",
    "investors": ["Coatue", "Addition", "Ribbit Capital"],
    "valuation": "$8.6B",
    "founded_date": "2014",
    "employee_count": "800+",
    "headquarters": "New York, USA",
    "website": "https://www.chainalysis.com",
    "last_funding_date": "2022-05-10"
  }
]
```

### CSV Output

Headers: name, description, category, funding_amount, funding_round, investors, valuation, founded_date, employee_count, headquarters, website, last_funding_date

### Summary Output

```
================================================================================
STARTUP RESEARCH SUMMARY
================================================================================

Total Startups: 25

Startups by Category:
  - Blockchain: 8
  - Crypto: 7
  - Web3: 6
  - AI Web3: 4

Total Funding Collected: $4,823,000,000
Average Funding per Startup: $192,920,000

Top 10 Funded Startups:
  1. Blockchain.com - $620M (Valuation: $14B)
  2. Dapper Labs - $605M (Valuation: $7.6B)
  3. Fireblocks - $550M (Valuation: $8B)
  ...

Top 10 Active Investors:
  1. a16z - 5 investments
  2. Coatue - 4 investments
  3. Sequoia Capital - 3 investments
  ...

================================================================================
```
