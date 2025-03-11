import docker
import platform
import os
import docker.errors
import dotenv
import database
import json
import logging
import webbrowser
from openai import OpenAI
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS


# Load the environment variables
dotenv.load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "default_secret")  # Secret key for session handling
CORS(app)

# Get the API key from the environment variables
API_KEY = os.getenv("API_KEY")

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

conversation_history = []

# SYSTEM_PROMPT = """
# You are an expert assistant tasked with providing precise, context-based answers from the given data.
# You are answering questions as a student advisor for the Masters Program AI in Society.
# Only respond with information explicitly available in the provided data, ensuring the response is specific, accurate, and free of any generalization, extrapolation, or assumptions.
# Retain as much detail and context from the original data as possible.
# If there is no fitting answer in the data, respond with an explanation that the question cannot be answered with the provided data and that they should try to reformulate the question.
# Only if there has not been any progress in the conversation in a while and the student question is relevant to the program, ask them to contact the study advisor at ais@sot.tum.de.
# """
SYSTEM_PROMPT = """
You are an advanced student advisor for the Masters Program AI in Society, designed to provide helpful, accurate information.
Only respond with information explicitly available in the provided data, ensuring the response is specific, accurate, and free of any generalization, extrapolation, or assumptions

ANSWERING PROCESS:
1. First analyze the question carefully to understand both the explicit request and implicit intent
2. When working with database information:
   - Look for relevant content even when wording differs from the query
   - Consider information from partial matches if they contain relevant details
   - Connect related information across multiple sources when appropriate
   - Prioritize accuracy but aim to be helpful even with imperfect matches

3. When formulating responses:
   - Provide comprehensive answers by synthesizing information from all relevant sources
   - Structure your response logically, addressing each part of multi-part questions
   - Use natural, conversational language while maintaining accuracy

4. For questions without clear matches:
   - Suggest potential reformulations of their question
   - Provide closely related information with in the extracted data, that might help
   - Ristrict online search only to TUM website for additional info and mention the source only if it from the TUM website. 
Remember: Your goal is to be as helpful as possible while staying grounded in the available information. When uncertain, be transparent about limitations while still attempting to address the user's needs.
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
    global conversation_history

    # print(f"\n\n Database info\n\n{database_context}")

    # Add the database context to the user message

    print("\n\nconversation_history\n\n", conversation_history)

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

    # print("\n\nMessage histroy\n\n", conversation_history)

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
    print(f"\n\nReformulated question:{response_text}")
    return response_text

@app.route("/")
def index():
    """ Serve the chatbot HTML file. """
    return render_template("Index.html")


@app.route("/query", methods=["POST"])
def handle_query():
    request_data = request.json
    question = request_data.get("query", "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # STEP 4: Remfomulate the question according to conversation history context
    reformulated_question = refomulate_question(question, conversation_history)

    # logging.debug(f"Reformulated question: {reformulated_question}")

    # STEP 4: Search the database for the question
    similar_questions = database.find_closest_questions(reformulated_question, top_n=5)
    # logging.debug(f"Found {len(similar_questions)} similar questions in the database.")

    similar_pdf_sections = database.find_closest_pdf(reformulated_question, top_n=5)
    # logging.debug(f"Found {len(similar_pdf_sections)} similar PDF sections in the database.")

    database_context = {
        "Information from emails": similar_questions,
        "Information from PDFs": similar_pdf_sections,
    }

    database_context_text = json.dumps(database_context, indent=4)
    # logging.debug(f"Database context: {database_context_text}")

    # logging.debug(f"Using conversation history: {conversation_history}")

    # STEP 5: Generate an answer using the language model
    response = send_gpt_request(question, database_context_text)
    # logging.debug(f"Received response: {response}")

    return jsonify({"response": response})
    # print(response)


def open_browser():
    """ Open the Flask application in the default web browser. """
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
