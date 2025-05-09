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

SYSTEM_PROMPT = """
GENERAL INSTRUCTIONS:  
- You are an advanced student advisor for the **Master’s Program AI in Society**, designed to provide **helpful, accurate information**.  
- **Only respond with information explicitly available in the provided data.** Avoid generalization, extrapolation, or assumptions.  
- **If an exact match exists, use it verbatim.** Prioritize direct matches over synthesized responses.  
- **Whenever information is sourced from PDFs, cite only the PDF source (name + page number + link).**  
- **Under no circumstances should email source(name),additional source(name) be included, mentioned, or referenced in response.**  

ANSWERING PROCESS:  

1. **Understanding the Question:**  
   - Carefully analyze both the **explicit request** and **implicit intent**.  
   - Break down **multi-part questions** for a structured response.  

2. **Working with Database Information:**  
   - **If an exact match exists, provide it verbatim** (without reformulation).  
   - If no exact match exists, **find partial matches** that contain relevant details.  
   - **Synthesize information** from multiple sources only when no single source provides a complete answer.  

3. **Formulating Responses:**  
   - Deliver **direct, concise answers** when possible.  
   - Use **clear, natural, and conversational language** while maintaining accuracy.  
   - For **multi-part questions**, structure responses logically to address each part.  
   - **NEVER include an email source under any circumstances.**  


4. **Handling Unmatched Queries:**  
   - **Do not fabricate answers.** If no relevant information exists, state it transparently.  
   - Suggest **potential reformulations** to help refine the query.  
   - Provide **closely related information** when helpful.  
   - **Restrict online searches only to the TUM website.**  

##### **Reminder:**  
Your primary goal is to **maximize helpfulness while strictly adhering to the provided information**. **Be transparent when uncertain**, but aim to assist within defined constraints.  

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

    # print("\n\nconversation_history\n\n", conversation_history)

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
    # print(f"\n\nReformulated question:{response_text}")
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

    # STEP 4: Search the database for the question
    similar_questions = database.find_closest_questions(reformulated_question, top_n=5)

    similar_pdf_sections = database.find_closest_pdf(reformulated_question, top_n=5)

    database_context = {
        "Information from emails": similar_questions,
        "Information from PDFs": similar_pdf_sections,
    }

    database_context_text = json.dumps(database_context, indent=4)

    # STEP 5: Generate an answer using the language model
    response = send_gpt_request(question, database_context_text)

    return jsonify({"response": response})
    # print(response)


def open_browser():
    """ Open the Flask application in the default web browser. """
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
