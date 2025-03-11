from flask import Flask, request, jsonify, render_template, session
from database import find_closest_questions, find_closest_pdf
import openai
import os
import webbrowser
from flask_cors import CORS
import logging
import uuid
import json

# Initialize Flask app
app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "default_secret")  # Secret key for session handling
CORS(app)

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

# Set OpenAI API key
API_KEY = os.getenv("API_KEY")
client = openai.OpenAI(api_key=API_KEY)

# Dictionary to store chat history per session (Limited to 5 messages per session)
conversation_history = []

SYSTEM_PROMPT = """
You are an expert assistant tasked with providing precise, context-based answers from the given data. Use a professional tone and ensure the response is concise, accurate, and aligned with the user's intent.
You are answering questions as a student advisor for the Masters Program AI in Society.
Only respond with information explicitly available in the provided data, ensuring the response is specific, accurate, and free of any generalization, extrapolation, or assumptions.
Match the query to the most relevant knowledge source and prioritize clarity in the response.
Retain as much detail and context from the original data as possible.
Generate prompts which are only related to the question prompt and try to keep the answers very simple to the database and do not over enhance it. Never mention the context the data is extracted from and if there is no data found in both the datasets then ask for a better prompt.    
Only if there has not been any progress in the conversation in a while and the student question is relevant to the program, ask them to contact the study advisor at ais@sot.tum.de.
"""


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
    response = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.4)

    # Get the response text from the response
    response_text = response.choices[0].message.content

    return response_text

def generate_profound_answer(question, email_context, pdf_context):
    """
    Generate an answer using OpenAI API with conversational memory.
    """
    # Retrieve conversation history (last 5 exchanges)
    history = conversation_history[-5:]

    # Build message history for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add user question FIRST to ensure the model focuses on it
    user_message = f'Answer the following question: "{question}" using the following database information:\n\n\n {email_context}\n\n{pdf_context}'
    messages.append({"role": "user", "content": user_message})

    for exchange in history:
        if "question" in exchange and "response" in exchange:
            messages.append({"role": "user", "content": exchange["question"]})
            messages.append({"role": "assistant", "content": exchange["response"]})

        print(history)

    # Call OpenAI API
    try:
        response = client.chat.completions.create(model="gpt-4o", messages=messages, temperature=0.4)
        answer = response.choices[0].message.content.strip()

        # Get the numver of tokens used
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens

        print(f"\n\n\nPrompt tokens: {prompt_tokens}, Completion tokens: {completion_tokens}, Total tokens: {total_tokens}\n\n")

        # Store latest interaction in chat history
        # conversation_history.setdefault(session_id, []).append({"question": question, "response": answer})
        # print(f"Chat_history:\n{conversation_history}")

        conversation_history.append({"question": question, "response": answer})
    
        return answer
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "An error occurred while processing your request."
        

@app.route("/")
def index():
    """ Serve the chatbot HTML file. """
    return render_template("Index.html")

@app.route("/query", methods=["POST"])
def handle_query():
    """
    Handle user queries, retrieve relevant context, and generate a response.
    """
    global conversation_history  # Ensure we modify the global history
    request_data = request.json
    question = request_data.get("query", "").strip()
    # session_id = request_data.get("session_id", str(uuid.uuid4()))  # Get or create session ID

    if not question:
        return jsonify({"error": "Question is required"}), 400
    

    # Reformulate question if necessary
    reformulated_question = refomulate_question(question, conversation_history)

    # Retrieve context from emails & PDFs
    closest_questions = find_closest_questions(reformulated_question, top_n=5)
    email_context = " ".join([q["answer_text"] for q in closest_questions]) if closest_questions else ""

    closest_pdfs = find_closest_pdf(reformulated_question, top_n=5)
    pdf_context = " ".join([p["pdf_text"] for p in closest_pdfs]) if closest_pdfs else ""

    # If no relevant context is found, return default response
    if not email_context and not pdf_context:
        return jsonify({"response": "No relevant information found."})

    # Generate response using OpenAI with conversation memory
    response_text = generate_profound_answer(question, email_context, pdf_context)

    return jsonify({"response": response_text})

def open_browser():
    """ Open the Flask application in the default web browser. """
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)