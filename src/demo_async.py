#!/usr/bin/env python3
"""
Demo script to test the async book description generator with a small subset
"""

import asyncio
import json

from libs.async_generator import AsyncBookDescriptionGenerator


async def demo():
    """Run a demo with a small subset of items"""

    print("🎯 Demo: Async Book Description Generator")
    print("=" * 50)

    try:
        # Load items
        print("📖 Loading items...")
        with open("items.json", "r", encoding='UTF-8') as file:
            all_items = json.load(file)

        # Take only first 3 items for demo
        demo_items = all_items[:3]
        print(f"✅ Using {len(demo_items)} items for demo")

        # Show items we'll process
        print("\n📚 Items to process:")
        for i, item in enumerate(demo_items, 1):
            print(f"  {i}. {item['name']} (ID: {item['id']})")

        generator = AsyncBookDescriptionGenerator(max_workers=2)

        print("\n🚀 Starting processing...")
        print("⚙️  Configuration: 2 workers, async mode")
        print("-" * 50)

        # Process items
        results = await generator.process_items(
            demo_items,
            batch_size=3,  # Process all in one batch
            use_threading=False)

        # Save demo results
        demo_output = "demo_results.json"
        demo_failed = "demo_failed.json"

        await generator.save_results(results, demo_output)
        await generator.save_failed_items(demo_failed)

        print("\n🎉 Demo completed!")
        print(f"📄 Results saved to: {demo_output}")

        if generator.failed_items:
            print(f"❌ Failed items saved to: {demo_failed}")

        # Show sample results
        if results:
            print("\n📋 Sample result:")
            sample = results[0]
            print(f"  Title: {sample['name']}")
            print(
                f"  Description: {sample.get('description', 'N/A')[:100]}...")

    except FileNotFoundError:
        print("❌ Error: items.json not found!")
        print("Make sure you're running this from the src directory")
    except Exception as e:
        print(f"💥 Error: {e}")


if __name__ == "__main__":
    asyncio.run(demo())
