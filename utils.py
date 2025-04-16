from dataclasses import asdict, is_dataclass
from dotenv import load_dotenv
import os


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


class PromptLoader:
    def __init__(self, prompt_files: dict):
        """
        Initializes and loads prompts from the given file paths.

        :param prompt_files: A dictionary where keys are prompt identifiers (e.g., "coordinator")
                             and values are file paths to the prompt files.
        """
        self.prompts = {}
        for prompt_name, file_path in prompt_files.items():
            try:
                with open(file_path, "r") as f:
                    self.prompts[prompt_name] = f.read()
            except FileNotFoundError:
                print(f"Error: The file '{file_path}' for prompt '{prompt_name}' was not found.")
                self.prompts[prompt_name] = ""
            except Exception as e:
                print(f"An error occurred while reading '{file_path}' for prompt '{prompt_name}': {e}")
                self.prompts[prompt_name] = ""

    def get_prompt(self, prompt_name: str) -> str:
        """
        Retrieves the text of a loaded prompt by its key.

        :param prompt_name: The key corresponding to the desired prompt.
        :return: The prompt text, or an empty string if not found.
        """
        return self.prompts.get(prompt_name, "")


class ConfigManager:
    def __init__(self, env_file=".env"):
        try:
            load_dotenv(env_file)
        except Exception as e:
            print(f"Error loading environment file '{env_file}': {e}")

        self.vector_store_id = os.getenv("vector_store_id")
        if self.vector_store_id is None:
            print("Warning: 'vector_store_id' not found in the environment variables.")

    def get_vector_store_id(self):
        return self.vector_store_id