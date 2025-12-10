# Output Format Examples

This document shows examples of the different output formats available in the AI Startup Research Agent.

## Text Format (.txt)

The text format provides human-readable output that's perfect for copying and pasting into emails, documents, and reports.

### Regular Startup Research Example

```
================================================================================
STARTUP RESEARCH RESULTS
================================================================================
Generated: 2025-12-10 21:36:59
Total Startups: 2
================================================================================


################################################################################
STARTUP #1
################################################################################

Name: Chainalysis
Category: Blockchain
Description: Blockchain data platform providing investigation and compliance tools

Funding Information:
  Funding Amount: $366M
  Funding Round: Series F
  Valuation: $8.6B
  Date: N/A

Investors (3):
  - Coatue
  - Addition
  - Ribbit Capital

Company Details:
  Website: https://www.chainalysis.com
  Headquarters: New York, USA
  Founded: 2014
  Employees: N/A


################################################################################
STARTUP #2
################################################################################

Name: Alchemy
Category: Blockchain
Description: Blockchain developer platform powering millions of users

Funding Information:
  Funding Amount: $200M
  Funding Round: Series C1
  Valuation: $10.2B
  Date: N/A

Investors (3):
  - Lightspeed
  - Silver Lake
  - a16z

Company Details:
  Website: https://www.alchemy.com
  Headquarters: San Francisco, USA
  Founded: 2017
  Employees: N/A


================================================================================
END OF REPORT
================================================================================
```

### Seed Funding Research Example

```
================================================================================
SEED FUNDING ANALYSIS - INVESTOR-FOCUSED REPORT
================================================================================
Generated: 2025-12-10 21:37:26
================================================================================

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
Total Seed Funding Raised: $47,000,000
Average Seed Round Size: $23,500,000
Total Seed Rounds Tracked: 2
Unique Investors Identified: 6
Average Investors per Round: 3.0

MOST ACTIVE INVESTORS (TOP 20)
--------------------------------------------------------------------------------
 1. Animoca Brands                                     1 participations
 2. Dragonfly Capital                                  1 participations
 3. Khaled Vosti                                       1 participations
 4. Electric Capital                                   1 participations
 5. Sequoia Capital                                    1 participations
 6. Paradigm                                           1 participations

LEAD INVESTORS SUMMARY
--------------------------------------------------------------------------------

Investor: Animoca Brands
  Investments: 1
  Total Invested: $20,000,000
  Average Investment: $20,000,000

Investor: Electric Capital
  Investments: 1
  Total Invested: $27,000,000
  Average Investment: $27,000,000

FUNDING DATA SOURCES
--------------------------------------------------------------------------------

Source: Crunchbase
  Funding Rounds: 2
  Total Funding: $47,000,000
  Unique Investors: 6
  Top Investors: Dragonfly Capital, Sequoia Capital, Khaled Vosti, Animoca Brands, Paradigm

INDUSTRY BREAKDOWN
--------------------------------------------------------------------------------
  Blockchain                               1 startups
  NFT/Web3                                 1 startups

GEOGRAPHIC DISTRIBUTION
--------------------------------------------------------------------------------
  San Francisco, USA                       2 startups


================================================================================
DETAILED SEED FUNDING ROUNDS
================================================================================


################################################################################
FUNDING ROUND #1
################################################################################

Startup: Helium Foundation
Industry: Blockchain
Headquarters: San Francisco, USA
Description: Decentralized wireless network for IoT devices

Funding Details:
  Amount: $20M
  Round: Seed
  Announcement Date: 2023-06-15
  Timeline: Early Stage

Investor Information:
  Total Investors: 3
  Lead Investor: Animoca Brands
  Investor Type: ['VC Firms', 'Angel Investors']
  Average Investment per Investor: $6.67M

  All Investors (3):
    - Animoca Brands
    - Dragonfly Capital
    - Khaled Vosti

Data Source:
  Site: Crunchbase
  URL: https://www.crunchbase.com/organization/helium


================================================================================
END OF SEED FUNDING REPORT
================================================================================
```

## Usage Commands

### Export to Text Format Only

```bash
# Regular startup research
python main.py --categories blockchain --max-results 10 --output-format txt

# Seed funding research
python main.py --seed-funding --max-results 10 --output-format txt
```

### Export to All Formats (JSON, CSV, Excel, Text)

```bash
# Regular startup research
python main.py --categories blockchain crypto --output-format all

# Seed funding research
python main.py --seed-funding --output-format all
```

### View Summary Only (No Export)

```bash
# Regular startup research
python main.py --categories blockchain --summary-only

# Seed funding research
python main.py --seed-funding --summary-only
```

## Benefits of Text Format

1. **Copy & Paste Ready** - Easy to copy sections and paste into:
   - Email messages
   - Reports and documents
   - Presentations
   - Slack/Teams messages
   - Internal wikis

2. **No Special Software** - Opens in any text editor:
   - Notepad (Windows)
   - TextEdit (Mac)
   - vim/nano (Linux)
   - VS Code, Sublime Text, etc.

3. **Human Readable** - Clean formatting with:
   - 80-character width for easy reading
   - Clear section headers
   - Consistent indentation
   - Logical grouping of information

4. **Professional Layout** - Well-structured with:
   - Executive summaries
   - Investor insights
   - Detailed company information
   - Source attribution

5. **Search Friendly** - Easy to search with:
   - Standard text search (Ctrl+F / Cmd+F)
   - grep/find commands
   - Terminal searching
