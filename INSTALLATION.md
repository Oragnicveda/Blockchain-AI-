# Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 512MB minimum (2GB recommended)
- **Disk Space**: 100MB for application and dependencies

## Installation Steps

### Option 1: Standard Installation (Recommended)

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

#### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify Installation

```bash
python test_agent.py
```

If you see "All tests passed! ✓", you're ready to go!

### Option 2: Quick Installation

Use the provided setup script (Linux/macOS):

```bash
chmod +x setup.sh
./setup.sh
```

### Option 3: Docker Installation (Coming Soon)

```bash
docker build -t startup-research-agent .
docker run -it startup-research-agent
```

## Configuration (Optional)

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit Configuration

Open `.env` in your favorite editor and add API keys if you have them:

```bash
# Optional API Keys
OPENAI_API_KEY=your_openai_key_here
CRUNCHBASE_API_KEY=your_crunchbase_key_here
NEWS_API_KEY=your_news_api_key_here

# Performance Settings (defaults shown)
MAX_WORKERS=5
REQUEST_TIMEOUT=30
RATE_LIMIT_DELAY=1
```

**Note**: All API keys are optional. The agent works without them using built-in sample data.

## First Run

### Test the Installation

```bash
python test_agent.py
```

Expected output:
```
Testing AI Startup Research Agent...

1. Initializing agent...
   ✓ Agent initialized successfully

2. Testing data collection...
   ✓ Collected 3 startups

...

All tests passed! ✓
```

### Run Your First Research

```bash
# Basic run
python main.py

# Or with specific categories
python main.py --categories blockchain crypto
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Problem**: `ModuleNotFoundError: No module named 'pandas'`

**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: Permission Denied

**Problem**: `Permission denied` when running scripts

**Solution**: Make scripts executable:
```bash
chmod +x main.py test_agent.py run.sh
```

### Issue: Python Version Too Old

**Problem**: `SyntaxError` or version mismatch

**Solution**: Check Python version and upgrade if needed:
```bash
python --version  # Should be 3.8 or higher
```

Install Python 3.8+:
- **Ubuntu/Debian**: `sudo apt update && sudo apt install python3.8`
- **macOS**: `brew install python@3.8`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### Issue: SSL Certificate Error

**Problem**: SSL errors when fetching data

**Solution**: Update certificates:
```bash
pip install --upgrade certifi
```

### Issue: Rate Limiting

**Problem**: Getting rate limited by websites

**Solution**: Increase delay in `.env`:
```
RATE_LIMIT_DELAY=2  # Increase from 1 to 2 seconds
```

### Issue: Out of Memory

**Problem**: Script crashes with memory error

**Solution**: Reduce max results:
```bash
python main.py --max-results 25
```

## Updating

### Update from Git

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Check for Updates

```bash
git fetch origin
git log HEAD..origin/main --oneline
```

## Uninstallation

### Remove Virtual Environment

```bash
deactivate  # If currently activated
rm -rf venv
```

### Remove Application

```bash
cd ..
rm -rf <repository-directory>
```

## Development Installation

For contributors and developers:

```bash
# Clone repository
git clone <repository-url>
cd <repository-name>

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies + dev tools
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Install in editable mode
pip install -e .

# Run tests
pytest
```

## Platform-Specific Notes

### Linux

- Preferred platform, all features fully supported
- Use package manager for Python: `sudo apt install python3 python3-pip`

### macOS

- Fully supported
- Use Homebrew for easy Python installation: `brew install python3`
- Some security settings may require allowing script execution

### Windows

- Fully supported
- Use Windows Subsystem for Linux (WSL) for best experience
- Or use native Windows with Command Prompt or PowerShell
- Antivirus may flag downloads, add exception if needed

## Network Requirements

The agent requires internet access to:
- Download dependencies during installation
- Fetch news feeds (optional, can be disabled with `--no-news`)
- Access external APIs (if configured)

Firewall rules may need to allow:
- Outbound HTTPS (port 443)
- Outbound HTTP (port 80)

## Dependencies Explained

### Core Dependencies

- **pandas** (2.0.0+): Data manipulation and analysis
- **requests** (2.31.0+): HTTP library for API calls
- **beautifulsoup4** (4.12.0+): HTML parsing for web scraping
- **python-dotenv** (1.0.0+): Environment variable management

### Supporting Dependencies

- **openpyxl** (3.1.0+): Excel file export
- **feedparser** (6.0.10+): RSS/Atom feed parsing
- **fake-useragent** (1.4.0+): User agent rotation
- **tqdm** (4.66.0+): Progress bars
- **python-dateutil** (2.8.0+): Date parsing
- **lxml** (4.9.0+): XML/HTML processing
- **retry** (0.9.2+): Retry logic for HTTP requests

### Optional Dependencies

- **openai** (1.0.0+): For AI-powered features (requires API key)
- **selenium** (4.15.0+): For JavaScript-heavy scraping (advanced)
- **aiohttp** (3.9.0+): Async HTTP (future feature)

## Verification Checklist

After installation, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list`)
- [ ] Test script runs successfully (`python test_agent.py`)
- [ ] Main script shows help (`python main.py --help`)
- [ ] Output directory created (`ls output/`)
- [ ] .gitignore in place (excludes venv, output, logs)

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review error messages in `logs/` directory
3. Search existing issues on GitHub
4. Create a new issue with:
   - Error message
   - Operating system
   - Python version
   - Steps to reproduce

## Next Steps

Once installed:

1. Read [QUICKSTART.md](QUICKSTART.md) for basic usage
2. Browse [EXAMPLES.md](EXAMPLES.md) for code examples
3. Check [README.md](README.md) for full documentation
4. Review [OVERVIEW.md](OVERVIEW.md) for technical details

Happy researching! 🚀
