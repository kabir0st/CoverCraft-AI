import asyncio
import json
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

from libs.agent import GeneratorAgent

# Load KEY from .env
load_dotenv()
API_KEY = os.getenv("KEY")

if not API_KEY:
    raise EnvironmentError("KEY not found in .env")


@dataclass
class ProcessingStats:
    """Statistics for tracking processing progress"""
    total_items: int = 0
    completed: int = 0
    failed: int = 0
    in_progress: int = 0
    start_time: float = 0
    latest_failure_reason: str = ""

    def __post_init__(self):
        self.start_time = time.time()

    @property
    def elapsed_time(self) -> float:
        return time.time() - self.start_time

    @property
    def completion_rate(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.completed / self.total_items) * 100

    @property
    def failure_rate(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.failed / self.total_items) * 100


class RateLimitedBookGenerator:
    """Rate-limited async book description generator (40 requests/minute)"""

    def __init__(self,
                 max_workers: Optional[int] = None,
                 requests_per_minute: int = 40):
        self.api_key = API_KEY

        # Rate limiting configuration
        self.requests_per_minute = requests_per_minute
        self.min_request_interval = 60.0 / requests_per_minute  # 1.5 seconds

        # Adjust workers for rate limiting - conservative approach
        # Max 10 workers to ensure we don't overwhelm the API
        rate_safe_workers = min(10, requests_per_minute // 4)
        auto_workers = min(16, (os.cpu_count() or 1))
        self.max_workers = max_workers or min(rate_safe_workers, auto_workers)

        # Rate limiting state
        self.request_times = []
        self.last_request_time = 0
        self.rate_limit_lock = asyncio.Lock()

        # Processing state
        self.stats = ProcessingStats()
        self.stats_lock = threading.Lock()
        self.failed_items = []
        self.failed_items_lock = threading.Lock()

        # Progress display
        self.display_interval = 2.0  # seconds
        self.last_display_time = 0

        print(f"🚦 Rate limiting: {requests_per_minute} requests/minute")
        print(f"⏱️  Min interval: {self.min_request_interval:.1f}"
              f"s between requests")
        print(f"⚙️  Workers: {self.max_workers} (rate-limit optimized)")

    async def wait_for_rate_limit(self):
        """Ensure we don't exceed 40 requests per minute"""
        async with self.rate_limit_lock:
            current_time = time.time()

            # Remove requests older than 1 minute
            cutoff_time = current_time - 60
            self.request_times = [
                t for t in self.request_times if t > cutoff_time
            ]

            # If we have 40 requests in the last minute, wait
            if len(self.request_times) >= self.requests_per_minute:
                oldest_request = self.request_times[0]
                wait_time = oldest_request + 60 - current_time + 0.5  # Buffer
                if wait_time > 0:
                    print(f"\n🚦 Rate limit: waiting {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    current_time = time.time()

            # Ensure minimum interval between requests
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                await asyncio.sleep(wait_time)
                current_time = time.time()

            # Record this request
            self.request_times.append(current_time)
            self.last_request_time = current_time

    async def generate_single_description(
            self, item: Dict[str, Any],
            agent: GeneratorAgent) -> Union[Dict[str, Any], None]:
        """Generate description for a single item with rate limiting"""
        try:
            # Apply rate limiting before making request
            await self.wait_for_rate_limit()

            query = f"""
            Generate description for
            name: {item['name']}
            isbn: {item['barcode']}
            """

            # Update in_progress count
            with self.stats_lock:
                self.stats.in_progress += 1

            # Make the API call
            description = await agent.generate(query)

            # Create result item
            result_item = item.copy()
            result_item['description'] = description
            result_item['processed_at'] = datetime.now().isoformat()

            # Update completed count
            with self.stats_lock:
                self.stats.completed += 1
                self.stats.in_progress -= 1

            return result_item

        except Exception as e:
            error_msg = (f"Error processing item "
                         f"{item.get('id', 'unknown')}: {str(e)}")

            # Update failed count
            with self.stats_lock:
                self.stats.failed += 1
                self.stats.in_progress -= 1
                self.stats.latest_failure_reason = error_msg

            # Add to failed items
            failed_item = item.copy()
            failed_item['error'] = error_msg
            failed_item['failed_at'] = datetime.now().isoformat()

            with self.failed_items_lock:
                self.failed_items.append(failed_item)

            return None

    def display_progress(self, force: bool = False):
        """Display current progress with rate limiting info"""
        current_time = time.time()
        if not force and (current_time -
                          self.last_display_time) < self.display_interval:
            return

        with self.stats_lock:
            elapsed = self.stats.elapsed_time
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Calculate current request rate
            recent_requests = [
                t for t in self.request_times if t > current_time - 60
            ]
            current_rate = len(recent_requests)

            progress_text = (
                f"\r🚀 {self.stats.completed}/{self.stats.total_items} "
                f"({self.stats.completion_rate:.1f}%) | "
                f"✅ {self.stats.completed} | "
                f"❌ {self.stats.failed} | "
                f"⏳ {self.stats.in_progress} | "
                f"🚦 {current_rate}/{self.requests_per_minute}/min | "
                f"⏱️ {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
            print(progress_text, end="", flush=True)

            if self.stats.latest_failure_reason:
                print(f"\n💥 Latest: {self.stats.latest_failure_reason}")

        self.last_display_time = current_time

    async def process_batch_async(
            self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process batch with rate limiting"""
        print(f"\n🔄 Processing {len(items)} items (rate-limited)...")

        # Create agents
        agents = [
            GeneratorAgent(self.api_key)
            for _ in range(min(self.max_workers, len(items)))
        ]

        # Use smaller semaphore for rate limiting
        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_with_semaphore(item: Dict[str, Any],
                                         agent: GeneratorAgent):
            async with semaphore:
                return await self.generate_single_description(item, agent)

        # Create tasks
        tasks = []
        for i, item in enumerate(items):
            agent = agents[i % len(agents)]
            task = asyncio.create_task(process_with_semaphore(item, agent))
            tasks.append(task)

        # Process and collect results
        results = []
        progress_task = asyncio.create_task(self.progress_display_loop())

        try:
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                self.display_progress()
        finally:
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

        return results

    async def progress_display_loop(self):
        """Continuous progress display"""
        try:
            while True:
                self.display_progress()
                await asyncio.sleep(self.display_interval)
        except asyncio.CancelledError:
            pass

    async def process_items(self,
                            items: List[Dict[str, Any]],
                            batch_size: int = 10) -> List[Dict[str, Any]]:
        """Process all items with rate limiting"""

        self.stats.total_items = len(items)

        # Calculate estimated time
        estimated_minutes = (len(items) * self.min_request_interval) / 60

        print(f"\n🚀 Processing {len(items)} items with rate limiting")
        print(f"⚙️  Config: {self.max_workers} workers, "
              f"batch size {batch_size}")
        print(f"🚦 Rate limit: {self.requests_per_minute}/minute "
              f"({self.min_request_interval:.1f}s interval)")
        print(f"⏱️  Estimated time: {estimated_minutes:.1f} minutes")
        print("-" * 70)

        all_results = []
        batch_file = "batch_processed.json"

        # Initialize or load existing batch file
        try:
            with open(batch_file, "r", encoding='utf-8') as file:
                existing_data = json.load(file)
                print(f"📂 Found existing {batch_file} "
                      f"with {len(existing_data)} items")
        except FileNotFoundError:
            existing_data = []
            print(f"📂 Creating new {batch_file}")

        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(items) + batch_size - 1) // batch_size

            print(f"\n📦 Batch {batch_num}/{total_batches} "
                  f"({len(batch)} items)")

            batch_results = await self.process_batch_async(batch)
            all_results.extend(batch_results)

            # Save batch results immediately after processing
            if batch_results:
                existing_data.extend(batch_results)
                with open(batch_file, "w", encoding='utf-8') as file:
                    json.dump(existing_data,
                              file,
                              indent=2,
                              ensure_ascii=False)
                print(f"💾 Saved batch {batch_num} to {batch_file} "
                      f"({len(batch_results)} items)")

            print(f"\n✅ Batch {batch_num} done: "
                  f"{len(batch_results)} successful")

        # Final stats
        print("\n" + "=" * 70)
        self.display_progress(force=True)
        print("\n🎉 Processing complete!")
        print("📊 Final Results:")
        print(f"   ✅ Successful: {self.stats.completed}")
        print(f"   ❌ Failed: {self.stats.failed}")
        print(f"   📈 Success Rate: {100 - self.stats.failure_rate:.1f}%")
        print(f"   ⏱️  Total Time: {self.stats.elapsed_time:.1f} seconds")

        if self.stats.completed > 0:
            avg_time = self.stats.elapsed_time / self.stats.completed
            actual_rate = (self.stats.completed / self.stats.elapsed_time) * 60
            print(f"   ⚡ Avg Time/Item: {avg_time:.1f}s")
            print(f"   🚦 Actual Rate: {actual_rate:.1f} requests/minute")

        return all_results

    async def save_results(self,
                           results: List[Dict[str, Any]],
                           output_file: str = "items_with_descriptions.json"):
        """Save successful results"""
        print(f"\n💾 Saving {len(results)} results to {output_file}...")

        with open(output_file, "w", encoding='utf-8') as file:
            json.dump(results, file, indent=2, ensure_ascii=False)

        print(f"✅ Results saved to {output_file}")

    async def save_failed_items(self, failed_file: str = "failed_items.json"):
        """Save failed items"""
        if not self.failed_items:
            print("📝 No failed items to save.")
            return

        print(f"\n💾 Saving {len(self.failed_items)} failed items to "
              f"{failed_file}...")

        with open(failed_file, "w", encoding='utf-8') as file:
            json.dump(self.failed_items, file, indent=2, ensure_ascii=False)

        print(f"❌ Failed items saved to {failed_file}")


async def main():
    """Main function with rate limiting"""

    print("📚 Rate-Limited Book Description Generator")
    print("🚦 Configured for 40 requests per minute")
    print("=" * 60)

    try:
        # Load items
        print("📖 Loading items from items.json...")
        with open("items.json", "r", encoding='UTF-8') as file:
            items = json.load(file)
        print(f"✅ Loaded {len(items)} items")

        generator = RateLimitedBookGenerator(max_workers=12,
                                             requests_per_minute=40)

        # Process items
        results = await generator.process_items(items, batch_size=200)

        # Save results
        await generator.save_results(results, "items_with_descriptions.json")
        await generator.save_failed_items("failed_items.json")

        print("\n🎊 All done! Check output files for results.")

    except FileNotFoundError:
        print("❌ Error: items.json file not found!")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
