#!/usr/bin/env python3
"""
Main script to run the async book description generator with various options
"""

import asyncio
import json
import sys
import argparse
from libs.async_generator import AsyncBookDescriptionGenerator


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Async Book Description Generator")

    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=None,
        help="Number of concurrent workers (default: auto-detect)")

    parser.add_argument("--batch-size",
                        "-b",
                        type=int,
                        default=20,
                        help="Batch size for processing (default: 20)")

    parser.add_argument("--threading",
                        "-t",
                        action="store_true",
                        help="Use threading instead of async")

    parser.add_argument("--demo",
                        "-d",
                        action="store_true",
                        help="Run demo with first 5 items only")

    parser.add_argument("--input",
                        "-i",
                        default="items.json",
                        help="Input JSON file (default: items.json)")

    parser.add_argument("--output",
                        "-o",
                        default="items_with_descriptions.json",
                        help="Output file for successful results")

    parser.add_argument("--failed-output",
                        "-f",
                        default="failed_items.json",
                        help="Output file for failed items")

    return parser.parse_args()


async def main():
    """Main function"""
    args = parse_args()

    print("📚 Async Book Description Generator")
    print("=" * 60)

    try:
        # Load items
        print(f"📖 Loading items from {args.input}...")
        with open(args.input, "r", encoding='UTF-8') as file:
            all_items = json.load(file)

        # Use subset for demo
        if args.demo:
            items = all_items[:5]
            print(f"🎯 Demo mode: Using first {len(items)} items")
        else:
            items = all_items

        print(f"✅ Loaded {len(items)} items to process")

        # Create generator
        generator = AsyncBookDescriptionGenerator(max_workers=args.workers,
                                                  use_process_pool=False)

        # Display configuration
        print(f"\n⚙️  Configuration:")
        print(f"   Workers: {generator.max_workers}")
        print(f"   Batch Size: {args.batch_size}")
        print(f"   Mode: {'Threading' if args.threading else 'Async'}")
        print(f"   Input: {args.input}")
        print(f"   Output: {args.output}")
        print(f"   Failed Output: {args.failed_output}")

        # Process items
        results = await generator.process_items(items,
                                                batch_size=args.batch_size,
                                                use_threading=args.threading)

        # Save results
        await generator.save_results(results, args.output)
        await generator.save_failed_items(args.failed_output)

        # Final summary
        print(f"\n🎊 Processing complete!")
        print(f"📊 Summary:")
        print(f"   ✅ Successful: {len(results)}")
        print(f"   ❌ Failed: {generator.stats.failed}")
        print(f"   📈 Success Rate: {100 - generator.stats.failure_rate:.1f}%")
        print(f"   ⏱️  Total Time: {generator.stats.elapsed_time:.2f}s")

        if len(results) > 0:
            avg_time = generator.stats.elapsed_time / len(results)
            print(f"   ⚡ Avg Time/Item: {avg_time:.2f}s")

        print(f"\n📄 Files created:")
        print(f"   📝 Results: {args.output}")
        if generator.failed_items:
            print(f"   ❌ Failed: {args.failed_output}")

    except FileNotFoundError:
        print(f"❌ Error: {args.input} not found!")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
