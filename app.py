from agents import Agent, Runner, WebSearchTool, FileSearchTool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
import asyncio
import logging
from tools import look_for_pdf_files, read_pdf
from dotenv import load_dotenv
import os
from utils import to_serializable, PromptLoader, ConfigManager


########################################################################################################################
########################################################################################################################

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),           # Console output
        logging.FileHandler("log.txt")       # File output
    ]
)

config = ConfigManager()
vector_store_id = config.get_vector_store_id()

prompt_files = {
    "coordinator": "./prompts/coordinator.md",
    "file_search": "./prompts/file_search.md",
    "web_search": "./prompts/web_search.md",
    "user_input": "user_input.md"
}

prompt_loader = PromptLoader(prompt_files)
COORDINATOR_PROMPT = prompt_loader.get_prompt("coordinator")
FILE_SEARCH_PROMPT = prompt_loader.get_prompt("file_search")
WEB_SEARCH_PROMPT = prompt_loader.get_prompt("web_search")
USER_INPUT = prompt_loader.get_prompt("user_input")

########################################################################################################################
########################################################################################################################


web_search_agent = Agent(
    name="WebSearchAgent",
    instructions=(f"{RECOMMENDED_PROMPT_PREFIX} \n\n {WEB_SEARCH_PROMPT}"),
    tools=[WebSearchTool(), look_for_pdf_files, read_pdf]
)

file_search_agent = Agent(
    name="FileSearchAgent",
    instructions=(f"{RECOMMENDED_PROMPT_PREFIX} \n\n {FILE_SEARCH_PROMPT}"),
    tools=[
        FileSearchTool(
            vector_store_ids=[vector_store_id],
            max_num_results=5,
            include_search_results=True    
        )
    ]
)

coordinator = Agent(
    name="Coordinator",
    instructions=(f"{RECOMMENDED_PROMPT_PREFIX} \n\n {COORDINATOR_PROMPT}"),
    handoffs=[web_search_agent, file_search_agent]
)

web_search_agent.handoffs.extend([coordinator, file_search_agent])
file_search_agent.handoffs.extend([coordinator, web_search_agent])

########################################################################################################################
########################################################################################################################


async def async_generate():
    output = await Runner.run(
        starting_agent=coordinator,
        input=USER_INPUT,
    )
    return output

def compare_files():
    output = asyncio.run(async_generate())
    output.final_output = to_serializable(output.final_output)
    return {
        "result": "success",
        "text": output.final_output
    }

if __name__ == "__main__":
    output = compare_files()
    print("-" * 30)
    print()
    print(output["text"])
    print()
    print("-" * 30)
