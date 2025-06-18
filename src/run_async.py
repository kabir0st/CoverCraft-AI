#!/usr/bin/env python3
"""
Simple script to run the async book description generator
"""

import asyncio
import sys
import os
import json

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from libs.async_app import AsyncBookDescriptionGenerator


async def run_generator():
    """Run the async book description generator with custom settings"""

    print("🚀 Starting Async Book Description Generator")
    print("=" * 60)

    # Configuration - adjust these based on your system and needs
    MAX_WORKERS = 8  # Number of concurrent workers
    BATCH_SIZE = 10  # Items to process in each batch
    USE_THREADING = False  # Set to True to use threading instead of async

    try:
        # Load items
        print("📖 Loading items...")
        with open("items.json", "r", encoding='UTF-8') as file:
            items = json.load(file)

        print(f"✅ Loaded {len(items)} items")

        # Create generator
        generator = AsyncBookDescriptionGenerator(max_workers=MAX_WORKERS,
                                                  use_process_pool=False)

        # Process items
        results = await generator.process_items(items,
                                                batch_size=BATCH_SIZE,
                                                use_threading=USE_THREADING)

        # Save results
        await generator.save_results(results, "items_with_descriptions.json")
        await generator.save_failed_items("failed_items.json")

        print("\n🎉 Processing complete!")
        print(f"✅ Successfully processed: {len(results)} items")
        print(f"❌ Failed items: {generator.stats.failed}")

        if generator.stats.failed > 0:
            print("📄 Check 'failed_items.json' for details on failed items")

    except FileNotFoundError:
        print("❌ Error: items.json not found!")
        print("Make sure you're running this from the src directory")
    except Exception as e:
        print(f"💥 Error: {e}")


if __name__ == "__main__":
    asyncio.run(run_generator())
