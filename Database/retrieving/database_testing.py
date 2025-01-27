import docker
import platform
import os
import dotenv
import database
import json
import logging

from openai import OpenAI

# Load the environment variables
dotenv.load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv("API_KEY")

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

SYSTEM_PROMPT = """
You are an expert assistant tasked with providing precise, context-based answers from the given data.
Only respond with information explicitly available in the provided database, ensuring the response is specific, accurate, and free of any generalization, extrapolation, or assumptions.
Retain as much detail and context from the original data as possible. Do not mention the source of the data or add any external information.
If no relevant information is found in the database, respond with "NO DATA FOUND" and request a more specific query.
"""

DEBUG = True

conversation_history = []


def docker_is_running():
    """
    Check that the docker container named 'alina' is running

    Returns:
    - bool: True if the container is running, False otherwise
    """

    # Initialize the docker client according to the platform
    if platform.system() == "Windows":
        DOCKER_CLIENT = docker.DockerClient(base_url="npipe:////./pipe/docker_engine")
    elif platform.system() in ["Linux", "Darwin"]:
        DOCKER_CLIENT = docker.DockerClient(base_url="unix://var/run/docker.sock")
    else:
        raise Exception(f"Unsupported platform: {platform.system()}")

    # Get the list of containers
    containers = DOCKER_CLIENT.containers.list()

    # Get the names of the containers
    container_names = [container.name for container in containers]

    # Check if the container 'alina' is in the list of containers
    return "alina" in container_names


def send_gpt_request(user_message, database_context, model="gpt-4o", temperature=0.4):
    """
    Get a response from the language model

    Args:
    - prompt (str): The prompt to send to the language model

    Returns:
    - str: The response from the language model
    """

    # Add the database context to the user message
    user_message = f'Answer the following question: "{user_message}" using the following database information:\n\n\n {database_context}'

    messages = [
        {"role": "developer", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user", "content": [{"type": "text", "text": user_message}]},
    ]

    # Add the conversation history to the messages
    messages = conversation_history + messages

    # Send the prompt to the language model
    response = client.chat.completions.create(model=model, messages=messages, temperature=temperature)

    # Get the numver of tokens used
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    logging.debug(f"Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}, Total tokens: {total_tokens}")

    response_text = response.choices[0].message.content

    # Add the user message and response to the conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": response_text})

    # Return the response
    return response_text


if __name__ == "__main__":
    # Configure the logging
    logging.basicConfig(filename=".temp/database_testing.log", encoding="utf-8", level=logging.DEBUG, filemode="w")

    # Set logging level for httpcore, openai, urllib3, docker, and httpx to WARNING
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("docker").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # STEP 1: Check that docker is running
    logging.debug("Checking if the docker container 'alina' is running...")
    if not docker_is_running():
        logging.error("Docker container 'alina' not running. Use the start_docker.bat file to start the container.")
        raise Exception("Docker container 'alina' not running. Use the start_docker.bat file to start the container.")
    logging.debug("Docker container 'alina' is running.")

    # STEP 2: Check that the database is running and initialized
    logging.debug("Checking if the database is running and initialized...")
    if not database.check_database_status():
        logging.error("Database is not running or not initialized, see above error message.")
        raise Exception("Database is not running or not initialized, see above error message.")
    logging.debug("Database is running and initialized.")

    while True:
        # STEP 3: Get the input question from the user
        question = input("Enter a question: ")

        logging.debug(f"Received question: {question}")

        # STEP 4: Search the database for the question
        similar_questions = database.find_closest_questions(question, top_n=5)
        logging.debug(f"Found {len(similar_questions)} similar questions in the database.")

        similar_pdf_sections = database.find_closest_pdf(question, top_n=5)
        logging.debug(f"Found {len(similar_pdf_sections)} similar PDF sections in the database.")

        database_context = {
            "Information from emails": similar_questions,
            "Information from PDFs": similar_pdf_sections,
        }

        database_context_text = json.dumps(database_context, indent=4)
        logging.debug(f"Database context: {database_context_text}")

        logging.debug(f"Using conversation history: {conversation_history}")

        # STEP 5: Generate an answer using the language model
        response = send_gpt_request(question, database_context_text)
        logging.debug(f"Received response: {response}")

        print(response)


# TODO: Add message history context
