import asyncio
import base64
import os
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables from .env file
load_dotenv()


class BookInput(BaseModel):
    """
    Pydantic model for the incoming book data.
    image_bytes should be the raw bytes of the image file.
    """
    name: str
    author: str
    isbn: str
    image_bytes: bytes


# Models for parsing Perplexity API response
class PerplexityMessageContent(BaseModel):
    content: str


class PerplexityChoice(BaseModel):
    message: PerplexityMessageContent


class PerplexityUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int


class PerplexityResponse(BaseModel):
    """
    Pydantic model to validate and parse the response from Perplexity API.
    """
    choices: List[PerplexityChoice]
    usage: PerplexityUsage
    # You might find other fields like 'id', 'model', 'created', etc.
    # Add them here if you need to validate them.


# --- 2. The PerplexityBookDescGenerator Class (The Core Flow) ---


class PerplexityBookDescGenerator:
    """
    A class to generate and store book descriptions using Perplexity AI.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Perplexity API Key is required.")
        self.api_key = api_key
        # Perplexity's chat completions endpoint
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # In-memory storage for descriptions (ISBN -> description)
        self.book_descriptions: Dict[str, str] = {}
        # Perplexity model that supports vision (e.g., 'llama-3-sonar-large-32k-online')
        # Check Perplexity's documentation for the latest vision-capable models.
        self.vision_model = "llama-3-sonar-large-32k-online"

    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """
        Encodes image bytes to a Base64 string.
        """
        return base64.b64encode(image_bytes).decode('utf-8')

    async def generate_description(self, book_input: BookInput) -> str:
        """
        Generates a book description using Perplexity AI and stores it.

        Args:
            book_input: An instance of BookInput containing book details and image bytes.

        Returns:
            The generated book description string.

        Raises:
            httpx.HTTPStatusError: If the API request returns a non-2xx status code.
            httpx.RequestError: If an error occurs during the API request.
            Exception: For other unexpected errors.
        """
        print(
            f"Generating description for '{book_input.name}' (ISBN: {book_input.isbn})..."
        )

        # Step 1: Prepare the image for Perplexity
        # Perplexity's vision models can accept Base64 encoded images directly in the prompt.
        base64_image = self._encode_image_to_base64(book_input.image_bytes)
        # Assuming jpeg for demo. In a real app, detect image type.
        image_mime_type = "image/jpeg"

        # Step 2: Construct the Perplexity API payload
        # Messages array structure for vision models
        messages_payload = [{
            "role":
            "system",
            "content":
            "You are an expert literary assistant specializing in creating captivating and concise book descriptions. Analyze the provided book details and cover image to craft a compelling synopsis."
        }, {
            "role":
            "user",
            "content": [{
                "type":
                "text",
                "text":
                (f"Generate a compelling description (100-200 words) for the following book:\n"
                 f"Title: {book_input.name}\n"
                 f"Author: {book_input.author}\n"
                 f"ISBN: {book_input.isbn}\n\n"
                 f"Pay close attention to the attached book cover image. Integrate visual elements and the overall theme suggested by the cover into the description."
                 )
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_mime_type};base64,{base64_image}"
                }
            }]
        }]

        payload = {
            "model": self.vision_model,
            "messages": messages_payload,
            "max_tokens":
            300,  # Limit response length to prevent excessive billing / rambling
            "temperature":
            0.5,  # Controls creativity (0.0=more deterministic, 1.0=more creative)
        }

        # Step 3: Make the asynchronous API call to Perplexity
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url,
                                             headers=self.headers,
                                             json=payload,
                                             timeout=60.0)
                response.raise_for_status(
                )  # Raises an exception for 4xx/5xx responses

            # Step 4: Parse and validate the response using Pydantic
            perplexity_response_data = response.json()
            # Use Pydantic to validate the structure of the API response
            parsed_response = PerplexityResponse(**perplexity_response_data)

            if not parsed_response.choices:
                raise ValueError(
                    "Perplexity response did not contain any choices.")

            description = parsed_response.choices[0].message.content.strip()

            # Step 5: Save the description with ISBN as key
            self.book_descriptions[book_input.isbn] = description
            print(
                f"Successfully generated and saved description for ISBN: {book_input.isbn}"
            )
            return description

        except httpx.HTTPStatusError as e:
            print(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
            if e.response.status_code == 401:
                print("Error: Unauthorized. Check your Perplexity API key.")
            elif e.response.status_code == 429:
                print("Error: Rate limit exceeded. Try again later.")
            raise
        except httpx.RequestError as e:
            print(f"An error occurred while requesting Perplexity API: {e}")
            raise
        except Exception as e:
            print(
                f"An unexpected error occurred during description generation: {e}"
            )
            raise

    def get_description(self, isbn: str) -> Optional[str]:
        """
        Retrieves a saved book description by its ISBN.
        """
        return self.book_descriptions.get(isbn)

    def list_all_descriptions(self) -> Dict[str, str]:
        """
        Returns all stored book descriptions.
        """
        return self.book_descriptions


# --- 3. Example Usage ---


async def main():
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print(
            "PERPLEXITY_API_KEY not found in environment variables. Please set it in a .env file."
        )
        return

    generator = PerplexityBookDescGenerator(api_key=api_key)

    # --- Prepare a dummy image for testing ---
    # In a real application, you would read an actual image file.
    # For now, let's create a tiny base64 encoded transparent PNG.
    # REPLACE THIS WITH A PATH TO A REAL BOOK COVER IMAGE FOR BETTER RESULTS!
    dummy_image_path = "path/to/your/book_cover.jpg"  # <--- IMPORTANT: Change this!

    if not os.path.exists(dummy_image_path):
        print(
            f"\n!--- WARNING: Dummy image '{dummy_image_path}' not found. Using a tiny placeholder image instead. ---!\n"
            "For best results, replace 'path/to/your/book_cover.jpg' with a real book cover image file."
        )
        # A tiny transparent GIF just so the API call doesn't fail due to missing image
        # This won't yield meaningful visual descriptions from Perplexity!
        dummy_image_bytes = base64.b64decode(
            "R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==")
    else:
        with open(dummy_image_path, "rb") as f:
            dummy_image_bytes = f.read()

    # --- Define some book data ---
    book1_data = {
        "name": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "isbn": "9780345391803",  # Example ISBN-13
        "image_bytes": dummy_image_bytes
    }

    book2_data = {
        "name": "1984",
        "author": "George Orwell",
        "isbn": "9780451524935",  # Another example ISBN-13
        "image_bytes": dummy_image_bytes
    }

    try:
        # Create Pydantic instances for validation
        book1_input = BookInput(**book1_data)
        book2_input = BookInput(**book2_data)

        print("\n--- Processing Book 1 ---")
        desc1 = await generator.generate_description(book1_input)
        print(f"\nGenerated Description for '{book1_input.name}':\n{desc1}\n")

        print("\n--- Processing Book 2 ---")
        desc2 = await generator.generate_description(book2_input)
        print(f"\nGenerated Description for '{book2_input.name}':\n{desc2}\n")

        # --- Retrieve descriptions from storage ---
        print("\n--- Retrieving Descriptions from Storage ---")
        retrieved_desc1 = generator.get_description(book1_input.isbn)
        print(
            f"Retrieved description for ISBN {book1_input.isbn}:\n{retrieved_desc1}\n"
        )

        retrieved_desc2 = generator.get_description(book2_input.isbn)
        print(
            f"Retrieved description for ISBN {book2_input.isbn}:\n{retrieved_desc2}\n"
        )

        # List all stored descriptions
        print("\n--- All Stored Descriptions ---")
        print(generator.list_all_descriptions())

    except Exception as e:
        print(f"\nAn error occurred during the overall process: {e}")


if __name__ == "__main__":
    # Ensure you are running this with Python 3.7+ for async/await support
    asyncio.run(main())
