# Async Book Description Generator

A high-performance, multi-threaded/async book description generator that utilizes multiple CPU cores and threads to process book descriptions in parallel with comprehensive progress tracking and error handling.

## Features

🚀 **Multi-Core Processing**: Utilizes all available CPU cores for maximum performance  
⚡ **Async/Threading Support**: Choose between async concurrency or thread-based processing  
📊 **Real-time Progress Tracking**: Live progress updates with completion rates and timing  
❌ **Error Handling**: Comprehensive error tracking with separate failed items logging  
💾 **Dual Output**: Successful results and failed items saved to separate JSON files  
🔧 **Configurable**: Adjustable worker counts, batch sizes, and processing modes  
- **Incremental Batch Saving**: Saves processed data after each batch to `batch_processed.json` for resilience.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
# Create a .env file with your API key
echo "KEY=your_perplexity_api_key_here" > .env
```

## Usage

### Quick Start

Run the async generator with default settings:

```bash
cd src
python run_generator.py # This script uses libs.async_generator.py
# For direct execution (if needed, usually run_generator.py is preferred):
# python libs/async_generator.py
```

### Custom Configuration

Use the run script for custom settings:

```bash
cd src
python run_generator.py # This is the primary script for custom async runs
# The file src/libs/run_async.py might be a specific utility or deprecated.
```

### Advanced Usage

```python
import asyncio
from libs.async_generator import AsyncBookDescriptionGenerator
import json

async def custom_run():
    # Load your items
    with open("src/items.json", "r") as f: # Assuming items.json is in src
        items = json.load(f)
    
    # Create generator with custom settings
    generator = AsyncBookDescriptionGenerator(
        max_workers=16,        # Number of concurrent workers
        use_process_pool=False # Use threading instead of multiprocessing
    )
    
    # Process items
    results = await generator.process_items(
        items,
        batch_size=25,         # Items per batch
        use_threading=False    # Use async instead of threading
    )
    
    # Save results
    await generator.save_results(results, "src/output.json") # Save in src
    await generator.save_failed_items("src/failed.json") # Save in src

# Run it
asyncio.run(custom_run())
```

## Configuration Options

### AsyncBookDescriptionGenerator Parameters

- **max_workers** (int, optional): Number of concurrent workers. Default: `min(32, CPU_cores + 4)`
- **use_process_pool** (bool): Whether to use process pool (currently not implemented)

### process_items Parameters

- **batch_size** (int): Number of items to process in each batch. Default: 50
- **use_threading** (bool): Use threading instead of async. Default: False

## Performance Tuning

### Recommended Settings by System

**High-end systems (16+ cores, 32+ GB RAM):**
```python
max_workers=32
batch_size=50
use_threading=False
```

**Mid-range systems (8-16 cores, 16+ GB RAM):**
```python
max_workers=16
batch_size=25
use_threading=False
```

**Low-end systems (4-8 cores, 8+ GB RAM):**
```python
max_workers=8
batch_size=10
use_threading=True
```

### Processing Modes

**Async Mode (Recommended)**
- Better for I/O-bound operations
- More efficient memory usage
- Better error handling
- Set `use_threading=False`

**Threading Mode**
- Better for CPU-bound operations
- May use more memory
- Good for systems with threading advantages
- Set `use_threading=True`

## Output Files

### Successful Results (`items_with_desc.json`)
```json
[
  {
    "id": 13625,
    "name": "Book Title",
    "barcode": "123456789",
    "description": "Generated description...",
    "processed_at": "2025-06-18T08:30:00.123456"
  }
]
```

### Failed Items (`failed_items.json`)
```json
[
  {
    "id": 9991,
    "name": "Failed Book",
    "barcode": "987654321",
    "error": "Error processing item 9991: API timeout",
    "failed_at": "2025-06-18T08:31:00.123456"
  }
]
```

## Progress Tracking

The generator provides real-time progress updates:

```
🚀 Progress: 45/100 (45.0%) | ✅ Success: 43 | ❌ Failed: 2 (2.0%) | ⏳ In Progress: 8 | ⏱️ Time: 00:02:30
```

### Progress Indicators

- **Progress**: Current completion percentage
- **Success**: Number of successfully processed items
- **Failed**: Number of failed items with failure rate
- **In Progress**: Currently processing items
- **Time**: Elapsed processing time

## Error Handling

The system handles various types of errors:

1. **API Errors**: Network timeouts, rate limits, invalid responses
2. **Data Errors**: Malformed input data, missing fields
3. **System Errors**: Memory issues, threading problems

All errors are:
- Logged with detailed error messages
- Saved to `failed_items.json` with timestamps
- Tracked in real-time progress updates
- Displayed as the latest failure reason

## Monitoring and Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Failed Items

```python
import json

# Load and analyze failed items
with open("failed_items.json", "r") as f:
    failed = json.load(f)

# Group by error type
error_types = {}
for item in failed:
    error = item.get("error", "Unknown")
    error_types[error] = error_types.get(error, 0) + 1

print("Error Summary:")
for error, count in error_types.items():
    print(f"  {error}: {count} items")
```

## Performance Metrics

The generator tracks and displays:

- **Total processing time**
- **Average time per item**
- **Success/failure rates**
- **Throughput (items per second)**

Example output:
```
📊 Final Stats:
   ✅ Successful: 95
   ❌ Failed: 5
   📈 Success Rate: 95.0%
   ⏱️  Total Time: 120.45 seconds
   ⚡ Average Time per Item: 1.27 seconds
```

## Troubleshooting

### Common Issues

**1. "KEY not found in .env"**
- Ensure your `.env` file exists and contains `KEY=your_api_key`

**2. High failure rates**
- Check your API key validity
- Reduce `max_workers` to avoid rate limiting
- Increase delays between requests

**3. Memory issues**
- Reduce `batch_size`
- Reduce `max_workers`
- Use `use_threading=True`

**4. Slow performance**
- Increase `max_workers` (if system can handle it)
- Increase `batch_size`
- Use `use_threading=False` for I/O-bound operations

### Getting Help

1. Check the console output for detailed error messages
2. Review `failed_items.json` for specific failure reasons
3. Adjust configuration based on your system capabilities
4. Monitor system resources (CPU, memory) during processing

## System Requirements

- Python 3.8+
- 4+ GB RAM (8+ GB recommended)
- Multi-core CPU (4+ cores recommended)
- Stable internet connection
- Valid Perplexity API key

## License

This project is part of the Perplexity Book Description Generator suite.