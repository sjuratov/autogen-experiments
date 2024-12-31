from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
import asyncio
from dotenv import load_dotenv
import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

# Load environment variables from a .env file
load_dotenv()

# Access environment variables
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')
AZURE_OPENAI_API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION')

async def main() -> None:
    # Define meal planner agent

    model_client=AzureOpenAIChatCompletionClient(
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
        model=AZURE_OPENAI_DEPLOYMENT,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        #api_key=AZURE_OPENAI_API_KEY,
        azure_ad_token_provider=token_provider,
    )

    meal_planner = AssistantAgent(
        name="meal_planner",
        model_client=model_client,
        system_message="""
        You are helpful AI assistant, specialist in creating nutritious and delicious meal plans.
        You are a culinary enthusiast dedicated to promoting healthy eating habits, you have extensive knowledge of nutrition and a passion for crafting delightful meals.
        Your meal plan will include breakfast, lunch and dinner with nutritional information for each meal.
        You will not plan for snacks.
        """
    )

    # Define groceries shopper agent
    groceries_shopper = AssistantAgent(
        name="groceries_shopper",
        model_client=model_client,
        system_message="""
        You are helpful AI assistant, specialist in making sure that all ingredients are readily available for cooking.
        You are a meticulous organizer with a keen eye for detail, you excel at sourcing high-quality ingredients and ensuring the pantry is always stocked.
        You will wait for meal_planner to create meal plan, and then you will create a comprehensive shopping list with quantities and specific items needed for the weekend meal plan.
        """
    )

    # Define a team with termination condition.
    agent_team = RoundRobinGroupChat(
        [meal_planner, groceries_shopper],
        max_turns=2
        )

    # Get user input from the console.
    task = """
    Create a weekend meal plan for 55 years adult that balances nutrition and taste. One day it will be 'pasta' day, the other day will be 'stake' day.
    """

    # Run the team and stream messages to the console.
    stream = agent_team.run_stream(task=task)
    await Console(stream)

asyncio.run(main())