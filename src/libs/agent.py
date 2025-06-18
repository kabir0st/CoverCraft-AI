from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from libs.utils import clear_text


class BookData(BaseModel):
    title: str = Field(description="The title of the book")
    barcode: str = Field(description="Library barcode of the book")


class GeneratorAgent:

    def __init__(self, api_key):
        if not api_key:
            raise ValueError('API needed for generator agent.')
        self.api_key = api_key
        with open('system_prompt.txt', 'r', encoding='utf-8') as file:
            system_prompt = file.read()
        self.model = OpenAIModel(
            "sonar-pro",
            provider=OpenAIProvider(base_url="https://api.perplexity.ai",
                                    api_key=self.api_key),
        )

        # Initialize the agent
        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
        )

    async def generate(self, user_prompt) -> str:
        """"
        Generate Book description based on image and
        name and isbn.
        """
        result = await self.agent.run(user_prompt=user_prompt)
        return clear_text(result.output)
