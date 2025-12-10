# Quick Start Guide

Get up and running with the AI Startup Research Agent in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd <repository-name>

# 2. Create and activate virtual environment (recommended)
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## First Run

Run the agent with default settings:

```bash
python main.py
```

This will:
- Research blockchain, crypto, Web3, AI, DeFi, and NFT startups
- Collect funding information and key metrics
- Generate a summary report
- Export results to `output/` directory in JSON, CSV, and Excel formats

## View Results

Check the `output/` directory for your results:

```bash
ls output/
```

You'll find files like:
- `startups_20240101_120000.json`
- `startups_20240101_120000.csv`
- `startups_20240101_120000.xlsx`

## Common Use Cases

### Research Specific Categories

```bash
# Research only blockchain startups
python main.py --categories blockchain

# Research blockchain and crypto
python main.py --categories blockchain crypto

# Research Web3 and AI
python main.py --categories web3 ai
```

### Limit Results

```bash
# Get top 20 startups per category
python main.py --max-results 20
```

### Export to Specific Format

```bash
# Export only as JSON
python main.py --output-format json

# Export only as CSV
python main.py --output-format csv

# Export only as Excel
python main.py --output-format xlsx
```

### Quick Summary

```bash
# Just show summary without exporting
python main.py --summary-only
```

## Test the Installation

Run the test script to verify everything works:

```bash
python test_agent.py
```

## Configuration (Optional)

For enhanced features, configure API keys:

```bash
# 1. Copy the example environment file
cp .env.example .env

# 2. Edit .env and add your API keys
nano .env  # or use your preferred editor
```

Available API keys (all optional):
- `OPENAI_API_KEY` - For AI-powered analysis
- `CRUNCHBASE_API_KEY` - For enhanced startup data
- `NEWS_API_KEY` - For news aggregation

## Programmatic Usage

Use the agent in your own Python scripts:

```python
from agent import StartupResearchAgent

# Initialize
agent = StartupResearchAgent()

# Research startups
results = agent.research_startups(
    categories=['blockchain', 'web3'],
    max_results=30
)

# Export results
agent.export_results(results, format='json')

# Print summary
agent.print_summary(results)
```

## Troubleshooting

### ImportError: No module named 'agent'

Make sure you're in the project directory and have activated the virtual environment:

```bash
cd /path/to/project
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Missing dependencies

Reinstall requirements:

```bash
pip install -r requirements.txt --upgrade
```

### Permission denied

Make sure the script is executable:

```bash
chmod +x main.py
chmod +x test_agent.py
```

## Next Steps

- Read [EXAMPLES.md](EXAMPLES.md) for more usage examples
- Check [README.md](README.md) for detailed documentation
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Getting Help

- Check the logs in `logs/` directory for debugging
- Review error messages in the console
- Make sure all dependencies are installed correctly

## Sample Output

After running the agent, you'll see output like:

```
════════════════════════════════════════════════════════════════
   AI Startup Research Agent
   Blockchain | Crypto | Web3 | AI
════════════════════════════════════════════════════════════════

============================================================
Researching BLOCKCHAIN startups
============================================================
Collecting data from web sources...
Collected 3 startups for blockchain

...

════════════════════════════════════════════════════════════════
STARTUP RESEARCH SUMMARY
════════════════════════════════════════════════════════════════

Total Startups: 25

Startups by Category:
  - Blockchain: 8
  - Crypto: 7
  - Web3: 6
  ...

✓ Exported JSON: output/startups_20240101_120000.json
✓ Exported CSV: output/startups_20240101_120000.csv
✓ Exported XLSX: output/startups_20240101_120000.xlsx

✓ Research complete! Collected data on 25 startups
```

Enjoy researching startups! 🚀
