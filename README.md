# AI Agent for Blockchain/Crypto/Web3 Startup Research

An intelligent agent that researches and collects data on blockchain, cryptocurrency, AI, and Web3 startups that have received funding, including key metrics and company information.

## Features

- 🔍 Automated research of blockchain, crypto, AI, and Web3 startups
- 💰 Funding information collection (rounds, amounts, investors)
- 📊 Key metrics tracking (valuation, employee count, founding date, etc.)
- 🤖 AI-powered data extraction and analysis
- 📁 Multiple export formats (JSON, CSV, Excel)
- 🔄 Configurable data sources and search parameters

## Key Metrics Collected

- Company Name
- Description
- Category (Blockchain, Crypto, AI, Web3)
- Funding Amount
- Funding Round
- Investors
- Valuation
- Founding Date
- Employee Count
- Headquarters Location
- Website
- Social Media Links
- Last Funding Date

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd <repository-name>

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with the following:

```
# Optional API Keys for enhanced data collection
OPENAI_API_KEY=your_openai_api_key
CRUNCHBASE_API_KEY=your_crunchbase_key (optional)
```

## Usage

### Basic Usage

```bash
# Run the agent with default settings
python main.py

# Run with specific categories
python main.py --categories blockchain crypto web3

# Run with custom output format
python main.py --output-format json

# Run with maximum results limit
python main.py --max-results 100
```

### Programmatic Usage

```python
from agent.startup_research_agent import StartupResearchAgent

# Initialize the agent
agent = StartupResearchAgent()

# Research startups
results = agent.research_startups(
    categories=['blockchain', 'crypto', 'web3', 'ai'],
    max_results=50
)

# Export results
agent.export_results(results, format='csv', filename='startups.csv')
```

## Output

Results are saved in the `output/` directory:
- `startups_YYYYMMDD_HHMMSS.json` - JSON format
- `startups_YYYYMMDD_HHMMSS.csv` - CSV format
- `startups_YYYYMMDD_HHMMSS.xlsx` - Excel format

## Project Structure

```
.
├── agent/
│   ├── __init__.py
│   ├── startup_research_agent.py    # Main agent orchestrator
│   ├── data_collectors/             # Data collection modules
│   │   ├── __init__.py
│   │   ├── web_scraper.py
│   │   ├── api_client.py
│   │   └── news_aggregator.py
│   ├── processors/                  # Data processing modules
│   │   ├── __init__.py
│   │   ├── data_parser.py
│   │   └── data_validator.py
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       ├── logger.py
│       └── config.py
├── output/                          # Output directory for results
├── main.py                          # Entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore file
└── README.md                        # This file
```

## Data Sources

The agent collects data from multiple sources:
- Public startup databases
- News articles and press releases
- Company websites
- Social media platforms
- Public APIs (when available)

## Disclaimer

This tool is for research purposes only. Please respect rate limits, terms of service, and robots.txt files of the websites being accessed. Always verify information from multiple sources.

## License

MIT License
