from agents import Agent, Runner, WebSearchTool, FileSearchTool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
import asyncio
import logging
from tools import look_for_pdf_files, read_pdf
from dotenv import load_dotenv
import os
from utils import to_serializable
load_dotenv()

## loading environment variables
class ConfigManager:
    def __init__(self, env_file=".env"):
        load_dotenv(env_file)
        self.vector_store_id = os.getenv("vector_store_id")

    def get_vector_store_id(self):
        return self.vector_store_id

## logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),           # Console output
        logging.FileHandler("log.txt")       # File output
    ]
)

## loading prompts
try:
    with open("./prompts/coordinator.md", "r") as f:
        COORDINATOR_PROMPT = f.read()
except FileNotFoundError:
    print("Error: The file './prompts/coordinator.md' was not found.")
    COORDINATOR_PROMPT = ""
except Exception as e:
    print(f"An error occurred while reading './prompts/coordinator.md': {e}")
    COORDINATOR_PROMPT = ""

try:
    with open("./prompts/file_search.md", "r") as f:
        FILE_SEARCH_PROMPT = f.read()
except FileNotFoundError:
    print("Error: The file './prompts/file_search.md' was not found.")
    FILE_SEARCH_PROMPT = ""
except Exception as e:
    print(f"An error occurred while reading './prompts/file_search.md': {e}")
    FILE_SEARCH_PROMPT = ""

try:
    with open("./prompts/web_search.md", "r") as f:
        WEB_SEARCH_PROMPT = f.read()
except FileNotFoundError:
    print("Error: The file './prompts/web_search.md' was not found.")
    WEB_SEARCH_PROMPT = ""
except Exception as e:
    print(f"An error occurred while reading './prompts/web_search.md': {e}")
    WEB_SEARCH_PROMPT = ""

try:
    with open("user_input.md", "r") as f:
        USER_INPUT = f.read()
except FileNotFoundError:
    print("Error: The file 'user_input.md' was not found.")
    USER_INPUT = ""
except Exception as e:
    print(f"An error occurred while reading 'user_input.md': {e}")
    USER_INPUT = ""



config = ConfigManager()
vector_store_id = config.get_vector_store_id()



web_search_agent = Agent(
    name="WebSearchAgent",
    instructions=(f"{RECOMMENDED_PROMPT_PREFIX} \n\n {WEB_SEARCH_PROMPT}"),
    tools=[WebSearchTool(), look_for_pdf_files, read_pdf]
)

file_search_agent = Agent(
    name= "FileSearchAgent",
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
    name = "Coordinator",
    instructions=(f"{RECOMMENDED_PROMPT_PREFIX} \n\n {COORDINATOR_PROMPT}"),
    handoffs = [web_search_agent, file_search_agent]                   
)

web_search_agent.handoffs.append(coordinator)
web_search_agent.handoffs.append(file_search_agent)
file_search_agent.handoffs.append(coordinator)
file_search_agent.handoffs.append(web_search_agent)


async def async_generate():
    output = await Runner.run(
        starting_agent=coordinator,
        input = USER_INPUT,
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

    print ("-"*30)
    print()
    print (output["text"])
    print()
    print ("-"*30)