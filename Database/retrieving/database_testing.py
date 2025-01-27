import docker
import platform
import os
import dotenv
import database
import json

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


def send_gpt_request(messages, model="gpt-4o"):
    """
    Get a response from the language model

    Args:
    - prompt (str): The prompt to send to the language model

    Returns:
    - str: The response from the language model
    """

    # Send the prompt to the language model
    response = client.chat.completions.create(model=model, messages=messages)

    # Return the response
    return response.choices[0].message


def create_gpt_mesages(user_message, database_info, history=None):
    user_message = f'Answer the following question: "{user_message}" using the following database information:\n\n\n {database_info}'

    messages = [
        {"role": "developer", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user", "content": [{"type": "text", "text": user_message}]},
    ]

    return messages


if __name__ == "__main__":
    # STEP 1: Check that docker is running
    if not docker_is_running():
        raise Exception("Docker container 'alina' not running. Use the start_docker.bat file to start the container.")

    # STEP 2: Check that the database is running and initialized
    if not database.check_database_status():
        raise Exception("Database is not running or not initialized, see above error message.")

    # STEP 3: Get the input question from the user
    question = input("Enter a question: ")

    if DEBUG:
        print(f"Answering question: \"{question}\"")

    # STEP 4: Search the database for the question
    similar_questions = database.find_closest_questions(question, top_n=3)
    similar_pdf_sections = database.find_closest_pdf(question, top_n=3)

    if DEBUG:
        print(f"Found {len(similar_questions)} similar questions in the database:")
        for similar_question in similar_questions:
            print(f"Question: {similar_question['question_text']}")
            print(f"Answer: {similar_question['answer_text']}")
            print(f"Source: {similar_question['source']}")
            print("Distance:" + str(similar_question['distance']))

        print(f"Found {len(similar_pdf_sections)} similar PDF sections in the database:")
        for similar_pdf_section in similar_pdf_sections:
            print(f"Section: {similar_pdf_section['pdf_text']}")
            print(f"Source: {similar_pdf_section['source']}")
            print("Distance:" + str(similar_pdf_section['distance']))

    database_result = similar_questions + similar_pdf_sections

    # STEP 5: Generate an answer using the language model
    messages = create_gpt_mesages(question, similar_pdf_sections)
    response = send_gpt_request(messages)

    print(response)
