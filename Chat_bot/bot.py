from flask import Flask, request, jsonify, render_template
from database import find_closest_questions, find_closest_pdf, add_question
import openai
import os
import webbrowser
from threading import Timer
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__, static_folder='static')  # Set static folder
CORS(app)

# Set OpenAI API key
openai.api_key = os.getenv('API_KEY')

def generate_profound_answer(question, context):
    """
    Generate a profound answer using OpenAI API.
    """
    prompt = f"Using the following context:\n\n{context}\n\nAnswer the question: {question}"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an expert assistant providing information from the given context. Use a professional tone and ensure the response is concise, accurate, and aligned with the user's intent. Match the query to the most relevant knowledge source and prioritize clarity in the response. Generate prompts which are only related to the question prompt and try to keep the answers very simple to the database and do not over enhance it. Never mention the context the data is extracted from and if there is no data found in both the datasets then ask for a better prompt.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content

@app.route('/')
def index():
    """
    Serve the chatbot HTML file.
    """
    return render_template('Index.html')

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Handle a query, search databases, and return the answer.
    """
    request_data = request.json
    question = request_data.get("query", "")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    # Search the questions database first
    closest_questions = find_closest_questions(question, top_n=5)
    context = ""

    if closest_questions:
        # Use answers from the questions database as context
        context = "\n".join([q["answer_text"] for q in closest_questions])
    else:
        # If not found, search the PDF database
        closest_pdfs = find_closest_pdf(question, top_n=5)

        if closest_pdfs:
            # Use answers from the PDFs as context
            context = "\n".join([p["answer_text"] for p in closest_pdfs])

            # Take the best answer and save it to the email database
            best_pdf = closest_pdfs[0]
            new_question = best_pdf['pdf_text']
            new_answer = best_pdf['answer_text']
            new_source = best_pdf['source']

            # Save to the email database
            add_question(new_question, new_answer, new_source)
        else:
            # No result found in either database
            return jsonify({"answer": "No relevant information found."})

    # Generate a profound answer using OpenAI
    response = generate_profound_answer(question, context)

    # Return only the AI-generated answer
    return jsonify({"response": response})

def open_browser():
    """
    Open the Flask application in the default web browser.
    """
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Start the browser in a separate thread
    # Timer(1, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
