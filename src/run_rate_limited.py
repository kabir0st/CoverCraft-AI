#!/usr/bin/env python3
"""
Run the rate-limited book description generator (40 requests/minute)
"""

import asyncio
import argparse
import json
from rate_limited_generator import RateLimitedBookGenerator


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Rate-Limited Book Description Generator (40 req/min)")

    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=8,
        help="Number of workers (default: 8, max recommended: 10)")

    parser.add_argument("--batch-size",
                        "-b",
                        type=int,
                        default=10,
                        help="Batch size (default: 10)")

    parser.add_argument("--demo",
                        "-d",
                        action="store_true",
                        help="Demo mode with first 5 items")

    parser.add_argument("--input",
                        "-i",
                        default="items.json",
                        help="Input file (default: items.json)")

    return parser.parse_args()


async def main():
    """Main function"""
    args = parse_args()

    print("🚦 Rate-Limited Book Description Generator")
    print("📋 Configured for 40 requests per minute")
    print("=" * 50)

    try:
        # Load items
        print(f"📖 Loading items from {args.input}...")
        with open(args.input, "r", encoding='UTF-8') as file:
            all_items = json.load(file)

        # Demo mode
        if args.demo:
            items = all_items[:5]
            print(f"🎯 Demo mode: processing {len(items)} items")
        else:
            items = all_items

        print(f"✅ Loaded {len(items)} items")

        # Validate workers
        if args.workers > 10:
            print("⚠️  Warning: >10 workers may exceed rate limits")
            print("   Recommended: 8 workers or less")

        # Create generator
        generator = RateLimitedBookGenerator(max_workers=args.workers,
                                             requests_per_minute=40)

        # Process items
        results = await generator.process_items(items,
                                                batch_size=args.batch_size)

        # Save results
        output_file = "demo_results.json" if args.demo else "items_with_descriptions.json"
        failed_file = "demo_failed.json" if args.demo else "failed_items.json"

        await generator.save_results(results, output_file)
        await generator.save_failed_items(failed_file)

        print(f"\n🎉 Complete! Files saved:")
        print(f"   📝 Results: {output_file}")
        if generator.failed_items:
            print(f"   ❌ Failed: {failed_file}")

    except FileNotFoundError:
        print(f"❌ Error: {args.input} not found!")
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    except Exception as e:
        print(f"💥 Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
