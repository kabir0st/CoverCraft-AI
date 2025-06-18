import asyncio
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import threading
from datetime import datetime

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


class AsyncBookDescriptionGenerator:
    """Async book description generator with multi-core/thread support"""

    def __init__(self,
                 max_workers: Optional[int] = None,
                 use_process_pool: bool = False):
        self.api_key = API_KEY
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.use_process_pool = use_process_pool
        self.stats = ProcessingStats()
        self.stats_lock = threading.Lock()
        self.failed_items = []
        self.failed_items_lock = threading.Lock()

        # Progress display settings
        self.display_interval = 1.0  # seconds
        self.last_display_time = 0

    async def generate_single_description(
            self, item: Dict[str,
                             Any], agent: GeneratorAgent) -> Dict[str, Any]:
        """Generate description for a single item"""
        try:
            query = f"""
            Generate description for
            name: {item['name']}
            isbn: {item['barcode']}
            """

            # Update in_progress count
            with self.stats_lock:
                self.stats.in_progress += 1

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

            # Update failed count and latest failure reason
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

            raise Exception(error_msg)

    def display_progress(self, force: bool = False):
        """Display current progress statistics"""
        current_time = time.time()
        if not force and (current_time -
                          self.last_display_time) < self.display_interval:
            return

        with self.stats_lock:
            elapsed = self.stats.elapsed_time
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)

            print(
                f"\r🚀 Progress: {self.stats.completed}/"
                f"{self.stats.total_items} "
                f"({self.stats.completion_rate:.1f}%) | "
                f"✅ Success: {self.stats.completed} | "
                f"❌ Failed: {self.stats.failed} "
                f"({self.stats.failure_rate:.1f}%) | "
                f"⏳ In Progress: {self.stats.in_progress} | "
                f"⏱️  Time: {int(hours):02d}:{int(minutes):02d}:"
                f"{int(seconds):02d}",
                end="",
                flush=True)

            if self.stats.latest_failure_reason:
                print(
                    f"\n💥 Latest failure: {self.stats.latest_failure_reason}")

        self.last_display_time = current_time

    async def process_batch_async(
            self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of items using async concurrency"""
        print(f"🔄 Processing {len(items)} items using async "
              f"concurrency...")

        # Create agent instances for each worker
        agents = [
            GeneratorAgent(self.api_key)
            for _ in range(min(self.max_workers, len(items)))
        ]

        # Create semaphore to limit concurrent operations
        semaphore = asyncio.Semaphore(self.max_workers)

        async def process_with_semaphore(item: Dict[str, Any],
                                         agent: GeneratorAgent):
            async with semaphore:
                return await self.generate_single_description(item, agent)

        # Create tasks for all items
        tasks = []
        for i, item in enumerate(items):
            agent = agents[i % len(agents)]
            task = asyncio.create_task(process_with_semaphore(item, agent))
            tasks.append(task)

        # Process tasks and collect results
        results = []
        completed_tasks = 0

        # Start progress display task
        progress_task = asyncio.create_task(self.progress_display_loop())

        try:
            # Wait for all tasks to complete
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                completed_tasks += 1

                # Update display periodically
                if (completed_tasks % 5 == 0 or completed_tasks == len(tasks)):
                    self.display_progress()

        finally:
            # Cancel progress display task
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                pass

        return results

    async def progress_display_loop(self):
        """Continuously display progress updates"""
        try:
            while True:
                self.display_progress()
                await asyncio.sleep(self.display_interval)
        except asyncio.CancelledError:
            pass

    def process_batch_threaded(
            self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of items using thread pool"""
        print(f"🧵 Processing {len(items)} items using thread pool...")

        def process_item_sync(item: Dict[str, Any]) -> Dict[str, Any]:
            # Create agent for this thread
            agent = GeneratorAgent(self.api_key)
            # Run async function in new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.generate_single_description(item, agent))
            finally:
                loop.close()

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(process_item_sync, item): item
                for item in items
            }

            # Collect results as they complete
            for future in future_to_item:
                try:
                    result = future.result()
                    if result is not None:
                        results.append(result)
                except Exception as e:
                    print(f"Thread execution error: {e}")

                # Update display
                self.display_progress()

        return results

    async def process_items(
            self,
            items: List[Dict[str, Any]],
            batch_size: int = 50,
            use_threading: bool = False) -> List[Dict[str, Any]]:
        """Process all items with progress tracking"""

        self.stats.total_items = len(items)
        print(f"🚀 Starting processing of {len(items)} items...")
        print(
            print(f"⚙️  Configuration: max_workers={self.max_workers}, "
                  f"batch_size={batch_size}"))
        print(
            f"🔧 Processing mode: {'Threading' if use_threading else 'Async'}")
        print("-" * 80)

        all_results = []

        # Process items in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(items) + batch_size - 1) // batch_size

            print(
                print(f"\n📦 Processing batch {batch_num}/{total_batches} "
                      f"({len(batch)} items)..."))

            if use_threading:
                batch_results = self.process_batch_threaded(batch)
            else:
                batch_results = await self.process_batch_async(batch)

            all_results.extend(batch_results)

            # Display batch completion
            print(
                print(f"\n✅ Batch {batch_num} completed: "
                      f"{len(batch_results)} successful"))

        # Final progress display
        print("\n" + "=" * 80)
        self.display_progress(force=True)
        print("\n🎉 Processing completed!")
        print("📊 Final Stats:")
        print(f"   ✅ Successful: {self.stats.completed}")
        print(f"   ❌ Failed: {self.stats.failed}")
        print(f"   📈 Success Rate: {100 - self.stats.failure_rate:.1f}%")
        print(f"   ⏱️  Total Time: {self.stats.elapsed_time:.2f} seconds")

        if self.stats.completed > 0:
            avg_time = self.stats.elapsed_time / self.stats.completed
            print(f"   ⚡ Average Time per Item: {avg_time:.2f} seconds")

        return all_results

    async def save_results(self,
                           results: List[Dict[str, Any]],
                           output_file: str = "items_with_desc.json"):
        """Save successful results to JSON file"""
        print(
            f"\n💾 Saving {len(results)} successful results to {output_file}..."
        )

        with open(output_file, "w", encoding='utf-8') as file:
            json.dump(results, file, indent=2, ensure_ascii=False)

        print(f"✅ Results saved to {output_file}")

    async def save_failed_items(self, failed_file: str = "failed_items.json"):
        """Save failed items to separate JSON file"""
        if not self.failed_items:
            print("📝 No failed items to save.")
            return

        print(
            print(f"\n💾 Saving {len(self.failed_items)} failed items to "
                  f"{failed_file}..."))

        with open(failed_file, "w", encoding='utf-8') as file:
            json.dump(self.failed_items, file, indent=2, ensure_ascii=False)

        print(f"❌ Failed items saved to {failed_file}")


async def main():
    """Main function to run the async book description generator"""

    # Configuration
    MAX_WORKERS = min(16,
                      (os.cpu_count() or 1) * 2)  # Adjust based on your system
    BATCH_SIZE = 20  # Process items in batches
    USE_THREADING = False  # Set to True to use threading instead of async

    print("📚 Async Book Description Generator")
    print("=" * 50)
    print(f"🖥️  System Info: {os.cpu_count()} CPU cores detected")
    print(f"⚙️  Max Workers: {MAX_WORKERS}")
    print(f"📦 Batch Size: {BATCH_SIZE}")

    try:
        # Load items from items.json
        print("\n📖 Loading items from items.json...")
        with open("src/items.json", "r", encoding='UTF-8') as file:
            items = json.load(file)

        print(f"✅ Loaded {len(items)} items")

        # Create generator instance
        generator = AsyncBookDescriptionGenerator(max_workers=MAX_WORKERS,
                                                  use_process_pool=False)

        # Process all items
        results = await generator.process_items(items,
                                                batch_size=BATCH_SIZE,
                                                use_threading=USE_THREADING)

        # Save results
        await generator.save_results(results, "src/items_with_desc.json")
        await generator.save_failed_items("src/failed_items.json")

        print("\n🎊 All done! Check the output files for results.")

    except FileNotFoundError:
        print("❌ Error: items.json file not found!")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
