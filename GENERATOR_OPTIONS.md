# Book Description Generator Options

This project provides multiple ways to generate book descriptions with different performance and rate limiting characteristics.

## 📋 Available Generators

### 1. 🚦 Rate-Limited Generator (RECOMMENDED for Production)
**File**: `src/rate_limited_generator.py`

- **Rate Limit**: Strict 40 requests per minute
- **Workers**: 6-8 recommended (max 10)
- **Use Case**: Production, large datasets, shared API keys
- **Safety**: Guaranteed API compliance

```bash
# Quick start
python src/run_rate_limited.py # Or directly: python src/rate_limited_generator.py

# Command line
python src/run_rate_limited.py --workers 8 --batch-size 10

# Demo
python src/run_rate_limited.py --demo
```

### 2. ⚡ High-Performance Generator (Development/Testing)
**File**: [`src/libs/async_generator.py`](src/libs/async_generator.py)

- **Rate Limit**: None (system/API limited)
- **Workers**: Up to 32 workers
- **Use Case**: Development, testing, small datasets
- **Speed**: Maximum performance

```bash
# Quick start
python src/run_generator.py # This script uses libs.async_generator

# Command line
python src/run_generator.py --workers 16 --batch-size 25

# Demo
python src/run_generator.py --demo
```

### 3. 📝 Original Simple Generator
**File**: `src/app.py` (Note: This might be deprecated or for basic learning only, check project status)

- **Type**: Sequential processing
- **Use Case**: Understanding the basic workflow
- **Speed**: Slow (one at a time)

```bash
python src/app.py
```

## 🎯 Which Generator Should You Use?

### For Production Use
```bash
# Use rate-limited generator
python src/run_rate_limited.py --workers 8 --batch-size 10
```

**Why?**
- Respects API rate limits
- Reliable for large datasets
- Won't get your API key blocked
- Handles errors gracefully

### For Development/Testing
```bash
# Use high-performance generator with demo
python src/run_generator.py --demo --workers 4
```

**Why?**
- Fast feedback during development
- Good for testing changes
- Suitable for small datasets

### For Learning/Understanding
```bash
# Use original simple generator
python src/app.py
```

**Why?**
- Easy to understand code
- Shows basic workflow
- Good for learning the API

## 📊 Performance Comparison

| Generator | Speed | Safety | Workers | Best For |
|-----------|-------|--------|---------|----------|
| Rate-Limited | 40/min | High | 6-8 | Production |
| High-Performance | System Max | Medium | 16-32 | Development |
| Original | ~1/min | High | 1 | Learning |

## 🚀 Quick Start Commands

### Production Processing (Recommended)
```bash
# Process all items with rate limiting
python src/run_generator.py --rate-limited # Assuming run_generator.py handles this, or use direct script
# python src/run_rate_limited.py (This script might be deprecated)

# Conservative settings
python src/run_rate_limited.py --workers 6 --batch-size 8

# Test with demo first
python src/run_rate_limited.py --demo
```

### Development/Testing
```bash
# Fast processing for development
python src/run_generator.py --demo

# High performance for testing
python src/run_generator.py --workers 16 --batch-size 20
```

## 📁 Output Files

All generators create the same output structure:

### Successful Results
- **Rate-Limited**: `items_with_descriptions.json`
- **High-Performance**: `items_with_descriptions.json`
- **Original**: `items_with_desc.json`

### Failed Items
- **Rate-Limited**: `failed_items.json`
- **High-Performance**: `failed_items.json`
- **Original**: No separate failed file

## ⚙️ Configuration Guide

### Rate-Limited Generator Settings

```bash
# Conservative (safest)
python src/run_rate_limited.py --workers 4 --batch-size 5

# Balanced (recommended)
python src/run_rate_limited.py --workers 8 --batch-size 10

# Aggressive (maximum within limits)
python src/run_rate_limited.py --workers 10 --batch-size 15
```

### High-Performance Generator Settings

```bash
# Conservative
python src/run_generator.py --workers 8 --batch-size 10

# Balanced
python src/run_generator.py --workers 16 --batch-size 20

# Maximum
python src/run_generator.py --workers 32 --batch-size 50
```

## 🔧 Environment Setup

### Required Files
1. `.env` file with `KEY=your_open_router_api_key`
2. `src/items.json` with your book data
3. Python dependencies installed

### Installation
```bash
pip install -r requirements.txt
```

### Verify Setup
```bash
# Test imports
python -c "import sys; sys.path.append('src'); from libs.async_generator import AsyncBookDescriptionGenerator; print('✅ Async Setup OK'); from rate_limited_generator import RateLimitedBookGenerator; print('✅ Rate-Limited Setup OK')"
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

## 🛡️ Safety Recommendations

### Always Use Rate-Limited For:
- ✅ Production processing
- ✅ Large datasets (100+ items)
- ✅ Shared/company API keys
- ✅ Unattended processing
- ✅ Critical data processing

### High-Performance OK For:
- ✅ Development and testing
- ✅ Small datasets (< 50 items)
- ✅ Personal API keys
- ✅ One-time processing
- ✅ Performance testing

## 🚨 Common Issues and Solutions

### Rate Limiting Errors
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

### Import Errors
```
Error: Module not found
Solution: Run from project root directory
```

## 📚 Documentation

- **Rate-Limited Guide**: `RATE_LIMITING_GUIDE.md`
- **Usage Guide**: `USAGE_GUIDE.md`
- **Async README**: `README_ASYNC.md`
- **This Guide**: `GENERATOR_OPTIONS.md`

## 🎯 Recommended Workflow

### 1. Start with Demo
```bash
python src/run_rate_limited.py --demo
```

### 2. Test with Small Batch
```bash
python src/run_rate_limited.py --workers 4 --batch-size 5
```

### 3. Scale Up Gradually
```bash
python src/run_rate_limited.py --workers 8 --batch-size 10
```

### 4. Full Production Run
```bash
python src/run_rate_limited.py
```

This approach ensures reliable, safe processing of your book descriptions while respecting API limits and providing comprehensive progress tracking and error handling.