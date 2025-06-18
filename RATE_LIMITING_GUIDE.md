# Rate-Limited Book Description Generator

A specialized version of the async book description generator that respects API rate limits of **40 requests per minute**.

## 🚦 Rate Limiting Features

- **Strict Rate Control**: Ensures exactly 40 requests per minute maximum
- **Smart Timing**: 1.5-second minimum interval between requests
- **Request Tracking**: Monitors requests in rolling 60-second window
- **Auto-Throttling**: Automatically waits when rate limit is approached
- **Progress Monitoring**: Shows current request rate in real-time

## Quick Start

### Basic Usage
```bash
cd src
python run_rate_limited.py # Or directly: python src/rate_limited_generator.py
# Note: src/run_rate_limited.py might be deprecated.
# Consider using src/run_generator.py with rate-limiting flags if available.
```

### Command Line Interface
```bash
cd src
python run_rate_limited.py
```

### Demo Mode (5 items)
```bash
cd src
python run_rate_limited.py --demo
```

## Command Line Options

```bash
python run_rate_limited.py [OPTIONS]

Options:
  -w, --workers N      Number of workers (default: 8, max recommended: 10)
  -b, --batch-size N   Batch size (default: 10)
  -d, --demo           Demo mode with 5 items
  -i, --input FILE     Input file (default: src/items.json)
```

## Examples

### Conservative Processing (Recommended)
```bash
python run_rate_limited.py --workers 6 --batch-size 8
```

### Demo Test
```bash
python run_rate_limited.py --demo --workers 2
```

### Custom Input File
```bash
python run_rate_limited.py --input my_books.json --workers 8
```

## Rate Limiting Details

### How It Works

1. **Request Tracking**: Maintains a list of request timestamps
2. **Rolling Window**: Only considers requests from the last 60 seconds
3. **Pre-Request Check**: Waits if 40 requests already made in last minute
4. **Minimum Interval**: Ensures 1.5 seconds between consecutive requests
5. **Buffer Time**: Adds small buffer to prevent edge cases

### Rate Limiting Algorithm

```python
# Check if we've made 40 requests in last 60 seconds
if len(recent_requests) >= 40:
    wait_time = oldest_request + 60 - current_time + 0.5
    await asyncio.sleep(wait_time)

# Ensure minimum 1.5s interval
if time_since_last < 1.5:
    await asyncio.sleep(1.5 - time_since_last)
```

## Progress Display

The rate-limited version shows enhanced progress information:

```
🚀 45/100 (45.0%) | ✅ 43 | ❌ 2 | ⏳ 8 | 🚦 38/40/min | ⏱️ 00:02:30
```

### Progress Indicators

- **🚀 Progress**: Completed/Total (percentage)
- **✅ Success**: Successfully processed items
- **❌ Failed**: Failed items count
- **⏳ In Progress**: Currently processing
- **🚦 Rate**: Current requests per minute / limit
- **⏱️ Time**: Elapsed time

## Performance Expectations

### Processing Times

**For 100 items:**
- Theoretical minimum: ~4 minutes (with perfect 40/min rate)
- Realistic estimate: 5-6 minutes (including overhead)

**For 1000 items:**
- Theoretical minimum: ~42 minutes
- Realistic estimate: 45-50 minutes

### Recommended Settings

**Small datasets (< 50 items):**
```bash
python run_rate_limited.py --workers 4 --batch-size 5
```

**Medium datasets (50-200 items):**
```bash
python run_rate_limited.py --workers 6 --batch-size 8
```

**Large datasets (200+ items):**
```bash
python run_rate_limited.py --workers 8 --batch-size 10
```

## Configuration Guidelines

### Worker Count

- **Recommended**: 6-8 workers
- **Maximum**: 10 workers (higher may cause rate limit issues)
- **Minimum**: 2 workers (for reasonable parallelism)

### Batch Size

- **Small batches (5-8)**: Better for monitoring, easier to restart
- **Medium batches (10-15)**: Good balance of efficiency and control
- **Large batches (20+)**: More efficient but harder to track progress

## Error Handling

### Rate Limit Protection

The generator includes multiple layers of protection:

1. **Pre-request validation**
2. **Request counting**
3. **Automatic waiting**
4. **Buffer time addition**

### Common Scenarios

**Rate limit reached:**
```
🚦 Rate limit: waiting 2.3s...
```

**API timeout:**
```
💥 Latest: Error processing item 123: Request timeout
```

**Network error:**
```
💥 Latest: Error processing item 456: Connection failed
```

## Python API Usage

### Basic Usage
```python
import asyncio
from src.rate_limited_generator import RateLimitedBookGenerator # Assuming direct import if run from project root
# Or adjust based on how scripts in src/libs might call this
import json

async def process_with_rate_limit():
    # Load items
    with open("src/items.json", "r") as f: # Assuming items.json is in src
        items = json.load(f)
    
    # Create rate-limited generator
    generator = RateLimitedBookGenerator(
        max_workers=8,
        requests_per_minute=40
    )
    
    # Process items
    results = await generator.process_items(items, batch_size=10)
    
    # Save results
    await generator.save_results(results, "src/items_with_descriptions.json") # Save in src
    await generator.save_failed_items("src/failed_items.json") # Save in src

asyncio.run(process_with_rate_limit())
```

### Advanced Configuration
```python
import asyncio
from src.rate_limited_generator import RateLimitedBookGenerator # Assuming direct import

async def advanced_rate_limited():
    # Custom rate limiting
    generator = RateLimitedBookGenerator(
        max_workers=6,           # Conservative worker count
        requests_per_minute=35   # Even more conservative rate
    )
    
    # Load and process
    with open("src/items.json", "r") as f: # Assuming items.json is in src
        items = json.load(f)
    
    results = await generator.process_items(
        items,
        batch_size=8  # Smaller batches for better control
    )
    
    # Custom output files
    await generator.save_results(results, "src/rate_limited_results.json") # Save in src
    await generator.save_failed_items("src/rate_limited_failures.json") # Save in src
    
    # Print final statistics
    print(f"Final rate: {len(generator.request_times)} requests in last minute")

asyncio.run(advanced_rate_limited())
```

## Monitoring and Debugging

### Real-time Monitoring

The generator provides detailed real-time information:

- Current request rate
- Time until next request allowed
- Processing statistics
- Error tracking

### Debug Information

```python
# Check current rate limiting state
print(f"Requests in last minute: {len(generator.request_times)}")
print(f"Time since last request: {time.time() - generator.last_request_time}")
print(f"Min interval: {generator.min_request_interval}")
```

## Troubleshooting

### Still Getting Rate Limited?

1. **Reduce workers**: Try 4-6 workers instead of 8
2. **Increase intervals**: Modify `requests_per_minute` to 35
3. **Smaller batches**: Use batch size 5-8
4. **Check network**: Ensure stable internet connection

### Slow Processing?

This is expected with rate limiting! The generator prioritizes API compliance over speed.

**Expected rates:**
- ~40 items per minute (ideal conditions)
- ~35-38 items per minute (realistic with overhead)

### Memory Issues?

- Reduce batch size to 5
- Reduce workers to 4
- Process in smaller chunks

## Best Practices

### 1. Start Conservative
```bash
# Test with small settings first
python run_rate_limited.py --demo --workers 2
```

### 2. Monitor Progress
Watch the rate indicator: `🚦 38/40/min`
- Should stay below 40
- Consistent rate indicates healthy processing

### 3. Plan for Time
Rate limiting means slower processing:
- 100 items ≈ 5-6 minutes
- 500 items ≈ 25-30 minutes
- 1000 items ≈ 45-50 minutes

### 4. Handle Interruptions
The generator handles Ctrl+C gracefully and saves progress.

### 5. Backup Data
Always backup your `src/items.json` before processing.
Additionally, note that `batch_processed.json` will be created/updated in the `src` directory,
containing all successfully processed items saved incrementally after each batch.

## Comparison: Rate-Limited vs Regular

| Feature | Regular Generator | Rate-Limited Generator |
|---------|------------------|----------------------|
| Speed | Fast (limited by system) | Controlled (40/min max) |
| API Safety | Risk of rate limiting | Guaranteed compliance |
| Workers | Up to 32 | Recommended 6-8 |
| Use Case | Development/Testing | Production |
| Monitoring | Basic progress | Enhanced with rate info |

## When to Use Rate-Limited Version

✅ **Use Rate-Limited When:**
- Processing production data
- Using shared API keys
- Processing large datasets
- Need guaranteed API compliance
- Running unattended processes

❌ **Use Regular Version When:**
- Development and testing
- Small datasets (< 20 items)
- Have dedicated API limits
- Need maximum speed

The rate-limited version is the **recommended choice for production use** to ensure reliable, compliant processing of your book descriptions.