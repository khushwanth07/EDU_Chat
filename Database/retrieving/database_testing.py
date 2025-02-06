import docker
import platform
import os
import docker.errors
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
You are answering questions as a student advisor for the Masters Program AI in Society.
Only respond with information explicitly available in the provided data, ensuring the response is specific, accurate, and free of any generalization, extrapolation, or assumptions.
Retain as much detail and context from the original data as possible.
If there is no fitting answer in the data, respond with an explanation that the question cannot be answered with the provided data and that they should try to reformulate the question.
Only if there has not been any progress in the conversation in a while and the student question is relevant to the program, ask them to contact the study advisor at ais@sot.tum.de.
"""


def docker_is_running():
    """
    Check that the docker container named 'alina' is running

    Returns:
    - bool: True if the container is running, False otherwise
    """

    try:
        # Initialize the docker client according to the platform
        if platform.system() == "Windows":
            DOCKER_CLIENT = docker.DockerClient(base_url="npipe:////./pipe/docker_engine")
        elif platform.system() in ["Linux", "Darwin"]:
            DOCKER_CLIENT = docker.DockerClient(base_url="unix://var/run/docker.sock")
        else:
            raise Exception(f"Unsupported platform: {platform.system()}")
    except docker.errors.DockerException:
        raise Exception("Docker is not running. Please start the docker application.")

    # Get the list of containers
    containers = DOCKER_CLIENT.containers.list()

    # Get the names of the containers
    container_names = [container.name for container in containers]

    # Check if the container 'alina' is in the list of containers
    return "alina" in container_names


def send_gpt_request(user_question, database_context, model="gpt-4o", temperature=0.4):
    """
    Get a response from the language model

    Args:
    - prompt (str): The prompt to send to the language model

    Returns:
    - str: The response from the language model
    """

    # Add the database context to the user message
    user_message = f'Answer the following question: "{user_question}" using the following database information:\n\n\n {database_context}'

    # Add the conversation history to the messages
    messages = conversation_history + [
        {"role": "developer", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user", "content": [{"type": "text", "text": user_message}]},
    ]

    # Send the prompt to the language model
    response = client.chat.completions.create(model=model, messages=messages, temperature=temperature)

    # Get the numver of tokens used
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    logging.debug(
        f"Prompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}, Total tokens: {total_tokens}"
    )

    # Check if the total tokens used exceed the context window limit
    if total_tokens > 128000:
        logging.warning(
            f"Used more than 128,000 tokens. Context windowd may be truncated. Total tokens used: {total_tokens}"
        )

    # Get the response text from the response
    response_text = response.choices[0].message.content

    # Add the user message and response to the conversation history
    conversation_history.append({"role": "user", "content": [{"type": "text", "text": user_question}]})
    conversation_history.append({"role": "assistant", "content": [{"type": "text", "text": response_text}]})

    # Return the response
    return response_text


def refomulate_question(question, conversation_history):
    """
    Refomulate the question based on the conversation history

    Args:
    - question (str): The original question
    - conversation_history (list): The conversation history

    Returns:
    - str: The refomulated question
    """
    if conversation_history == []:
        return question

    messages = [
        {
            "role": "developer",
            "content": [{"type": "text", "text": "In the following you will be given a chatbot conversation history including questions and answers. Additionally, you will be given a new question. Your task is reformulate the new question, if it is a follow up question, so it can be understood without the context of the conversation history. This is used for searching similar questions in database."}],
        },
        {
            "role": "user",
            "content": [{"type": "text", "text": f"The new user question is: {question} and the conversation history is as follows: {conversation_history}"}],
        },
    ]

    # Send the prompt to the language model
    response = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.3)

    # Get the response text from the response
    response_text = response.choices[0].message.content

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

    conversation_history = []

    while True:

        # STEP 3: Get the input question from the user
        question = input("Enter a question: ")

        logging.debug(f"Received question: {question}")

        # STEP 4: Remfomulate the question according to conversation history context
        reformulated_question = refomulate_question(question, conversation_history)

        logging.debug(f"Reformulated question: {reformulated_question}")

        # STEP 4: Search the database for the question
        similar_questions = database.find_closest_questions(reformulated_question, top_n=5)
        logging.debug(f"Found {len(similar_questions)} similar questions in the database.")

        similar_pdf_sections = database.find_closest_pdf(reformulated_question, top_n=5)
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
