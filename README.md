# CoverCraft-AI

A high-performance, multi-threaded book description generator that uses the Open router API to generate detailed descriptions for books. This project offers multiple processing modes optimized for different use cases, from development testing to production-scale processing.

## 🚀 Features

- **Multiple Processing Modes**: Choose between rate-limited (production-safe) and high-performance generators
- **Async & Multi-threading Support**: Utilizes multiple CPU cores for maximum performance
- **Rate Limiting Compliance**: Built-in rate limiting to respect API limits (40 requests/minute)
- **Real-time Progress Tracking**: Live progress updates with completion rates and timing
- **Comprehensive Error Handling**: Detailed error tracking with separate failed items logging
- **Flexible Configuration**: Adjustable worker counts, batch sizes, and processing modes
- **Dual Output System**: Successful results and failed items saved to separate JSON files
- **Incremental Batch Saving**: Saves processed data after each batch to `batch_processed.json` for resilience.

## 📋 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone git@github.com:kabir0st/CoverCraft-AI.git
cd CoverCraft-AI

# Install dependencies
uv sync
```

### 2. Environment Setup

Create a `.env` file with your Open Router API key:

```bash
echo "KEY=your_open_router_api_key_here" > .env
```

### 3. Prepare Your Data

Ensure you have an [`items.json`](src/items.json) file in the [`src/`](src/) directory with your book data:

```json
[
  {
    "id": 13625,
    "name": "Book Title",
    "barcode": "123456789"
  }
]
```

### 4. Run the Generator

**For Production (Recommended):**
```bash
cd src
python run_rate_limited.py --demo
```

**For Development/Testing:**
```bash
cd src
python run_generator.py --demo
```

## 🎯 Which Generator Should You Use?

### 🚦 Rate-Limited Generator (Production)
- **File**: [`src/rate_limited_generator.py`](src/rate_limited_generator.py)
- **Rate Limit**: Strict 40 requests per minute
- **Workers**: 6-8 recommended
- **Use Case**: Production, large datasets, shared API keys
- **Safety**: Guaranteed API compliance

```bash
python src/run_rate_limited.py --workers 8 --batch-size 10
```

### ⚡ High-Performance Generator (Development)
- **File**: [`src/libs/async_generator.py`](src/libs/async_generator.py)
- **Rate Limit**: None (system/API limited)
- **Workers**: Up to 32 workers
- **Use Case**: Development, testing, small datasets
- **Speed**: Maximum performance

```bash
python src/run_generator.py --workers 16 --batch-size 25
```

### 📝 Simple Generator (Learning)
- **File**: [`src/app.py`](src/app.py)
- **Type**: Sequential processing
- **Use Case**: Understanding the basic workflow
- **Speed**: Slow (one at a time)

```bash
python src/app.py
```

## 📚 Documentation

This project includes comprehensive documentation for different aspects:

### Core Documentation
- **[Generator Options Guide](GENERATOR_OPTIONS.md)** - Complete comparison of all available generators
- **[Usage Guide](USAGE_GUIDE.md)** - Detailed usage instructions with examples and best practices
- **[Rate Limiting Guide](RATE_LIMITING_GUIDE.md)** - Specialized guide for production-safe rate-limited processing
- **[Async Generator Guide](README_ASYNC.md)** - High-performance async processing documentation

### Quick Reference Links
- [Installation & Setup](USAGE_GUIDE.md#quick-start)
- [Command Line Options](USAGE_GUIDE.md#command-line-options)
- [Performance Tuning](USAGE_GUIDE.md#performance-tuning)
- [Error Handling](USAGE_GUIDE.md#error-handling)
- [Python API Usage](USAGE_GUIDE.md#python-api-usage)

## 🔧 Configuration Examples

### Production Processing (Recommended)
```bash
# Safe, rate-limited processing
python src/run_rate_limited.py --workers 8 --batch-size 10

# Test first with demo
python src/run_rate_limited.py --demo
```

### Development/Testing
```bash
# Fast processing for development
python src/run_generator.py --demo --workers 4

# High performance testing
python src/run_generator.py --workers 16 --batch-size 20
```

### System-Specific Recommendations

**High-End Workstation (32+ cores, 64+ GB RAM)**
```bash
python src/run_generator.py --workers 32 --batch-size 50
```

**Standard Laptop (8-16 cores, 16+ GB RAM)**
```bash
python src/run_rate_limited.py --workers 8 --batch-size 10
```

**Budget System (4-8 cores, 8+ GB RAM)**
```bash
python src/run_rate_limited.py --workers 4 --batch-size 5
```

## 📊 Performance Comparison

| Generator | Speed | Safety | Workers | Best For |
|-----------|-------|--------|---------|----------|
| Rate-Limited | 40/min | High | 6-8 | Production |
| High-Performance | System Max | Medium | 16-32 | Development |
| Simple | ~1/min | High | 1 | Learning |

## 📁 Output Files

### Successful Results
- **Rate-Limited**: [`items_with_descriptions.json`](src/items_with_descriptions.json)
- **High-Performance**: [`items_with_descriptions.json`](src/items_with_descriptions.json)
- **Simple**: [`items_with_desc.json`](src/items_with_desc.json)

### Failed Items
- **Rate-Limited**: [`failed_items.json`](src/failed_items.json)
- **High-Performance**: [`failed_items.json`](src/failed_items.json)

## 🚨 Common Issues & Solutions

### API Rate Limiting
```
Error: Rate limit exceeded
Solution: Use rate-limited generator
Command: python src/run_rate_limited.py
```

### Memory Issues
```
Error: Out of memory
Solution: Reduce batch size and workers
Command: python src/run_rate_limited.py --workers 4 --batch-size 5
```

### API Key Issues
```
Error: KEY not found in .env
Solution: Create .env file with KEY=your_api_key
```

## 🛡️ Best Practices

### 1. Always Start with Demo
```bash
python src/run_rate_limited.py --demo
```

### 2. Use Rate-Limited for Production
- ✅ Production processing
- ✅ Large datasets (100+ items)
- ✅ Shared/company API keys
- ✅ Unattended processing

### 3. Monitor Progress
Watch for the rate indicator: `🚦 38/40/min`

### 4. Handle Interruptions
Both generators handle Ctrl+C gracefully and save progress.

### 5. Backup Important Data
Always backup your original [`items.json`](src/items.json) before processing.

## 🔍 Project Structure

```
CoverCraft-AI/
├── README.md                     # This file - main project overview
├── GENERATOR_OPTIONS.md          # Complete generator comparison guide
├── USAGE_GUIDE.md                # Detailed usage instructions
├── RATE_LIMITING_GUIDE.md        # Production-safe rate limiting guide
├── README_ASYNC.md               # High-performance async guide
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
└── src/                          # Source code directory
    ├── rate_limited_generator.py   # Production-safe rate-limited generator
    ├── run_generator.py          # CLI for async generator
    ├── run_rate_limited.py       # CLI for rate-limited generator (deprecated, use run_generator.py with options)
    ├── demo_async.py             # Demo script for async generator
    ├── items.json                # Input data file
    ├── system_prompt.txt         # System prompt for the generator
    └── libs/                     # Core library files
        ├── __init__.py
        ├── agent.py              # Core API interaction logic
        ├── async_app.py          # Async application (if applicable)
        ├── async_generator.py    # High-performance async generator
        ├── gen.py                # General generation utilities (if applicable)
        ├── run_async.py          # Runner for async operations (if applicable)
        ├── run_rate_limited.py   # Runner for rate-limited operations (if applicable, might be deprecated)
        └── utils.py              # Helper functions
```

## 📈 Processing Time Estimates

### Rate-Limited Generator (40/min)
- 50 items: ~2-3 minutes
- 100 items: ~5-6 minutes
- 500 items: ~25-30 minutes
- 1000 items: ~45-50 minutes

### High-Performance Generator (varies)
- 50 items: ~30 seconds - 2 minutes
- 100 items: ~1-4 minutes
- 500 items: ~5-20 minutes
- 1000 items: ~10-40 minutes

*Times depend on system specs and API response times*

## 🎯 Recommended Workflow

1. **Start with Demo**: [`python src/run_rate_limited.py --demo`](src/run_rate_limited.py)
2. **Test Small Batch**: [`python src/run_rate_limited.py --workers 4 --batch-size 5`](src/run_rate_limited.py)
3. **Scale Up Gradually**: [`python src/run_rate_limited.py --workers 8 --batch-size 10`](src/run_rate_limited.py)
4. **Full Production Run**: [`python src/run_rate_limited.py`](src/run_rate_limited.py)

## 🔧 System Requirements

- Python 3.12+
- 4+ GB RAM (8+ GB recommended)
- Multi-core CPU (4+ cores recommended)
- Stable internet connection
- Valid Open Router API key

## 📖 Getting Help

1. **Read the Documentation**: Start with the [Usage Guide](USAGE_GUIDE.md)
2. **Check Common Issues**: Review error messages and solutions above
3. **Examine Failed Items**: Check [`failed_items.json`](src/failed_items.json) for specific failures
4. **Try Conservative Settings**: Use fewer workers and smaller batches
5. **Test with Demo Mode**: Always test with demo mode first

## 🚀 Next Steps

1. **New Users**: Start with the [Usage Guide](USAGE_GUIDE.md)
2. **Production Users**: Read the [Rate Limiting Guide](RATE_LIMITING_GUIDE.md)
3. **Developers**: Check the [Async Generator Guide](README_ASYNC.md)
4. **Comparison Shopping**: Review [Generator Options](GENERATOR_OPTIONS.md)

---

**Remember**: It's better to process slowly and successfully than to fail fast! Always prioritize API compliance and data integrity over speed.