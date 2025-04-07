from agents import Agent, Runner, WebSearchTool, FileSearchTool, function_tool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
import requests
from bs4 import BeautifulSoup
import io
from PyPDF2 import PdfReader
from urllib.parse import urljoin
import asyncio
import json
import logging
from dataclasses import asdict, is_dataclass

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),           # Console output
        logging.FileHandler("log.txt")       # File output
    ]
)

def to_serializable(obj):
    """
    Recursively convert dataclass instances or other objects to dictionaries
    so they can be JSON serialized.
    """
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(item) for item in obj]
    # For any other type, try to convert it or simply return it
    return obj


@function_tool
def read_pdf(pdf_url: str):
    """
    Downloads a PDF from the provided URL in memory,
    reads it using PyPDF2, and extracts the text.
    """
    response = requests.get(pdf_url)
    response.raise_for_status()  # Validate download
    pdf_bytes = io.BytesIO(response.content)
    reader = PdfReader(pdf_bytes)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


@function_tool
def look_for_pdf_files():
    """
    Goes to the specified URL, parses the page for PDF download links,
    and returns the full URL of the syllabus PDF.
    """
    base_url = "https://casqb.org/ke-stazeni"
    response = requests.get(base_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    pdf_link = None
    # Loop through all anchor tags that have a download attribute
    for a in soup.find_all('a', download=True):
        download_attr = a.get('download')
        # Check if the download attribute ends with .pdf and contains the syllabus identifier
        if download_attr and download_attr.lower().endswith('.pdf') and "ISTQB_CTFL_Syllabus_CZ" in download_attr:
            href = a.get('href')
            pdf_link = urljoin(base_url, href)  # Ensure the link is absolute
            break

    if not pdf_link:
        raise ValueError("No matching PDF file was found on the page.")
    return pdf_link




web_search_agent = Agent(
    name="WebSearchAgent",
    instructions=(f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a WebSearchAgent. Your task is to create a summary of the contents of a PDF document.
    First use the 'look_for_pdf_files' tool to extract the PDF.
    Then use the 'read_pdf' tool to read the file in memory and extract its text.
    Finally, generate a summary of the extracted content.
    Send that summary to file_search_agent for comparison with a local file.
    """),
    tools=[WebSearchTool(), look_for_pdf_files, read_pdf]
)

file_search_agent = Agent(
    name= "FileSearchAgent",
    instructions=(f"""{RECOMMENDED_PROMPT_PREFIX}
                  You are a FileSearchAgent. Your task is to compare the content of a PDF file with a local file.
                  You will retrieve the content of the PDF file from the Coordinator.
                  Use FileSearchTool to read the content of a vector store file.
                  Compare it with the content of the PDF file you retrieved from Coordinator.
                  """),
    tools=[
        FileSearchTool(
            vector_store_ids=["vs_67dddf290f988191aef04b7d4c0bd480"],
            max_num_results=5,             # Optional: Limit the number of results returned.
            include_search_results=True    # Optional: Include search results in the output.
        )
    ]
)

coordinator = Agent(
    name = "Coordinator",
    instructions = (f"""{RECOMMENDED_PROMPT_PREFIX} 
                    You are a coordinator agent, your task is to organize the workflow. 
                    First, get a file summary from the WebSearchAgent.
                    Then send that summary to the FileSearch Agent, and ask for comparison with local file.
                    Finally, output the comparison result."""),
    handoffs = [web_search_agent, file_search_agent]                   
)

web_search_agent.handoffs.append(coordinator)
web_search_agent.handoffs.append(file_search_agent)
file_search_agent.handoffs.append(coordinator)
file_search_agent.handoffs.append(web_search_agent)


async def async_generate():
    output = await Runner.run(
        starting_agent=coordinator,
        input = "Compare the content of the PDF named ISTQB_CTFL_Syllabus_CZ file with the local file that is located in a Playground Vector Store."
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