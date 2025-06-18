# Usage Guide: Async Book Description Generator

This guide shows you how to use the async book description generator in different ways.

## Quick Start

### 1. Basic Usage (Recommended)
```bash
cd src
python async_generator.py
```
This runs with default settings optimized for most systems.

### 2. Command Line Interface
```bash
cd src
python run_generator.py
```

### 3. Demo Mode (Test with 5 items)
```bash
cd src
python run_generator.py --demo
```

## Command Line Options

```bash
python run_generator.py [OPTIONS]

Options:
  -w, --workers N          Number of concurrent workers (default: auto)
  -b, --batch-size N       Items per batch (default: 20)
  -t, --threading          Use threading instead of async
  -d, --demo               Demo mode with 5 items only
  -i, --input FILE         Input JSON file (default: items.json)
  -o, --output FILE        Output file (default: items_with_descriptions.json)
  -f, --failed-output FILE Failed items file (default: failed_items.json)
```

## Examples

### High Performance (16+ cores)
```bash
python run_generator.py --workers 32 --batch-size 50
```

### Conservative (4-8 cores)
```bash
python run_generator.py --workers 8 --batch-size 10 --threading
```

### Custom Files
```bash
python run_generator.py --input my_books.json --output results.json
```

### Demo Test
```bash
python run_generator.py --demo --workers 2
```

## Python API Usage

### Basic Usage
```python
import asyncio
from async_generator import AsyncBookDescriptionGenerator
import json

async def process_books():
    # Load items
    with open("items.json", "r") as f:
        items = json.load(f)
    
    # Create generator
    generator = AsyncBookDescriptionGenerator(max_workers=16)
    
    # Process
    results = await generator.process_items(items)
    
    # Save
    await generator.save_results(results)
    await generator.save_failed_items()

asyncio.run(process_books())
```

### Advanced Configuration
```python
import asyncio
from async_generator import AsyncBookDescriptionGenerator
import json

async def advanced_processing():
    # Load items
    with open("items.json", "r") as f:
        items = json.load(f)
    
    # Create generator with custom settings
    generator = AsyncBookDescriptionGenerator(
        max_workers=24,           # 24 concurrent workers
        use_process_pool=False    # Use threading/async
    )
    
    # Process with custom batch settings
    results = await generator.process_items(
        items,
        batch_size=30,           # 30 items per batch
        use_threading=False      # Use async mode
    )
    
    # Save with custom filenames
    await generator.save_results(results, "my_results.json")
    await generator.save_failed_items("my_failures.json")
    
    # Print statistics
    print(f"Processed: {generator.stats.completed}")
    print(f"Failed: {generator.stats.failed}")
    print(f"Success Rate: {100 - generator.stats.failure_rate:.1f}%")

asyncio.run(advanced_processing())
```

## Performance Tuning

### System-Specific Recommendations

**High-End Workstation (32+ cores, 64+ GB RAM)**
```bash
python run_generator.py --workers 64 --batch-size 100
```

**Gaming PC (16-32 cores, 32+ GB RAM)**
```bash
python run_generator.py --workers 32 --batch-size 50
```

**Standard Laptop (8-16 cores, 16+ GB RAM)**
```bash
python run_generator.py --workers 16 --batch-size 25
```

**Budget System (4-8 cores, 8+ GB RAM)**
```bash
python run_generator.py --workers 8 --batch-size 10 --threading
```

### When to Use Threading vs Async

**Use Async (Default - Recommended)**
- Better for API calls (I/O bound)
- More memory efficient
- Better error handling
- Most use cases

**Use Threading**
- CPU-intensive processing
- Legacy system compatibility
- When async causes issues

```bash
# Use threading
python run_generator.py --threading
```

## Monitoring Progress

The generator shows real-time progress:

```
🚀 Progress: 45/100 (45.0%) | ✅ Success: 43 | ❌ Failed: 2 (2.0%) | ⏳ In Progress: 8 | ⏱️ Time: 00:02:30
```

### Progress Indicators Explained

- **Progress**: Items completed / Total items (percentage)
- **Success**: Successfully processed items
- **Failed**: Failed items with failure percentage
- **In Progress**: Currently being processed
- **Time**: Elapsed time in HH:MM:SS format

## Output Files

### Successful Results
File: `items_with_descriptions.json` (or custom name)

```json
[
  {
    "id": 13625,
    "name": "Book Title",
    "barcode": "123456789",
    "description": "AI-generated description of the book...",
    "processed_at": "2025-06-18T08:30:00.123456"
  }
]
```

### Failed Items
File: `failed_items.json` (or custom name)

```json
[
  {
    "id": 9991,
    "name": "Failed Book",
    "barcode": "987654321",
    "error": "Error processing item 9991: API timeout after 30s",
    "failed_at": "2025-06-18T08:31:00.123456"
  }
]
```

## Error Handling

### Common Errors and Solutions

**1. API Rate Limiting**
```
Error: Rate limit exceeded
Solution: Reduce --workers (try 4-8)
```

**2. Memory Issues**
```
Error: Out of memory
Solution: Reduce --batch-size (try 5-10)
```

**3. Network Timeouts**
```
Error: Request timeout
Solution: Check internet connection, reduce workers
```

**4. Invalid API Key**
```
Error: KEY not found in .env
Solution: Create .env file with KEY=your_api_key
```

### Retry Failed Items

```python
import asyncio
import json
from async_generator import AsyncBookDescriptionGenerator

async def retry_failed():
    # Load failed items
    with open("failed_items.json", "r") as f:
        failed_items = json.load(f)
    
    # Remove error fields to retry
    retry_items = []
    for item in failed_items:
        clean_item = {k: v for k, v in item.items() 
                     if k not in ['error', 'failed_at']}
        retry_items.append(clean_item)
    
    # Retry with conservative settings
    generator = AsyncBookDescriptionGenerator(max_workers=4)
    results = await generator.process_items(retry_items, batch_size=5)
    
    # Save retry results
    await generator.save_results(results, "retry_results.json")

asyncio.run(retry_failed())
```

## Best Practices

### 1. Start Small
Always test with demo mode first:
```bash
python run_generator.py --demo
```

### 2. Monitor System Resources
- Watch CPU usage (should be 70-90%)
- Monitor memory usage
- Check network bandwidth

### 3. Gradual Scaling
Start with conservative settings and increase:
```bash
# Start conservative
python run_generator.py --workers 4 --batch-size 5

# If stable, increase
python run_generator.py --workers 8 --batch-size 10

# Continue scaling up
python run_generator.py --workers 16 --batch-size 20
```

### 4. Handle Interruptions
The generator handles Ctrl+C gracefully and saves progress.

### 5. Backup Important Data
Always backup your original `items.json` before processing.

## Troubleshooting

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run your generator
```

### Check System Capabilities
```python
import os
print(f"CPU Cores: {os.cpu_count()}")
print(f"Recommended workers: {min(32, os.cpu_count() * 2)}")
```

### Analyze Failed Items
```python
import json
from collections import Counter

with open("failed_items.json", "r") as f:
    failed = json.load(f)

# Count error types
errors = [item.get("error", "Unknown") for item in failed]
error_counts = Counter(errors)

print("Error Summary:")
for error, count in error_counts.most_common():
    print(f"  {count}: {error}")
```

## Support

If you encounter issues:

1. Check this guide for solutions
2. Review error messages in console output
3. Examine `failed_items.json` for specific failures
4. Try conservative settings (fewer workers, smaller batches)
5. Test with demo mode first

Remember: It's better to process slowly and successfully than to fail fast!