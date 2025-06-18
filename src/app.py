# Example usage:
import asyncio
import json
import os

from dotenv import load_dotenv

from libs.agent import GeneratorAgent

# Load KEY from .env
load_dotenv()
API_KEY = os.getenv("KEY")

if not API_KEY:
    raise EnvironmentError("KEY not found in .env")

agent = GeneratorAgent(API_KEY)


async def main(query):
    description = await agent.generate(query)
    return description


if __name__ == "__main__":

    # Load items from items.json
    with open("items.json", "r", encoding='UTF-8') as file:
        items = json.load(file)
    for item in items:
        QUERY = f"""
            Generate description for
            name: {item['name']}
            isbn: {item['barcode']}
            """
        item['description'] = asyncio.run(main(query=QUERY))

    # Save updated items
    with open("items_with_desc.json", "w", encoding='utf-8') as file:
        json.dump(items, file, indent=2)
