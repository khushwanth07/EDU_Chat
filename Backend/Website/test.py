from flask import Flask, request, jsonify
import numpy as np
import openai
import psycopg2
import os
import json
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set your OpenAI API key
openai.api_key = os.getenv('API_KEY')

# Database connection details
db_config = {
    "database": os.getenv('DB_NAME'),
    "host": os.getenv('DB_HOST'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "port": os.getenv('DB_PORT'),
}

def _get_connection():
    """
    Establish and return a database connection.
    """
    return psycopg2.connect(**db_config)

def generate_query_embedding(query):
    """
    Generate an embedding for a given query using OpenAI.

    Parameters:
        query (str): The text of the query to embed.

    Returns:
        np.array: The embedding vector for the query.
    """
    response = openai.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype="float32")

def find_relevant_questions(query_embedding, top_n=5):
    """
    Find the most relevant questions from the database based on cosine similarity.

    Parameters:
        query_embedding (np.array): The embedding vector of the query.
        top_n (int): The number of closest matches to return.

    Returns:
        list[dict]: A list of dictionaries containing the closest questions and metadata.
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        find_query = '''
        SELECT id, question_text, answer_text, source_type, source,
               (embedding <=> %s::vector) AS distance
        FROM questions
        ORDER BY distance ASC
        LIMIT %s;
        '''
        cursor.execute(find_query, (query_embedding.tolist(), top_n))
        results = cursor.fetchall()
        return [
            {
                "id": row[0],
                "question_text": row[1],
                "answer_text": row[2],
                "source_type": row[3],
                "source": row[4],
                "distance": row[5],
            }
            for row in results
        ]
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()

def generate_response(query, relevant_questions):
    """
    Generate a response to a query using relevant questions as context.

    Parameters:
        query (str): The user's query.
        relevant_questions (list[dict]): The relevant questions fetched from the database.

    Returns:
        str: The generated response.
    """
    context = "\n".join([q["answer_text"] for q in relevant_questions])
    prompt = f"Using the following context:\n{context}\n\nAnswer the question: {query}"

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert assistant providing information from the given context. Use a professional tone and ensure the response is concise, accurate, and aligned with the user's intent. Match the query to the most relevant knowledge source and prioritize clarity in the response."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Handle incoming query requests (text-based or audio-based).

    Returns:
        Response: A JSON response containing the answer to the query.
    """
    query_data = request.json
    query = query_data.get("query", "")
# def handle_query(query_json):

#     query_data = json.loads(query_json)
#     query = query_data["query"]

    if not query:
        return jsonify({"error": "Query is required."}), 400

    # Generate embedding for the query
    query_embedding = generate_query_embedding(query)

    # Find relevant questions
    relevant_questions = find_relevant_questions(query_embedding)

    # Generate a response based on relevant questions
    response = generate_response(query, relevant_questions)
    return jsonify({"response": response})
    # return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
        # Simulated JSON input
    # query_json = json.dumps({"query": "What is the dealine for the course"})
    # response = handle_query(query_json)
    # print("Response:", response)