import faiss
import numpy as np
import openai
import json

# Set your OpenAI API key
openai.api_key = "api-key"

# Load the FAISS index
VECTOR_DB_PATH = "data.index"
index = faiss.read_index(VECTOR_DB_PATH)

# Load the text chunks for reference
with open("documents.txt", "r") as file:
    documents = file.read().split("\n---\n")

# Function to generate embedding for a query
def generate_query_embedding(query):
    response = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )
    return np.array(response["data"][0]["embedding"], dtype="float32")

# Function to find the most relevant chunks
def find_relevant_chunks(query_embedding, top_n=3):
    distances, indices = index.search(np.array([query_embedding]), top_n)
    results = [(documents[idx], distances[0][i]) for i, idx in enumerate(indices[0])]
    return results

# Function to generate a response
def generate_response(query, relevant_chunks):
    context = "\n".join([chunk[0] for chunk in relevant_chunks])
    prompt = f"Using the following context:\n{context}\n\nAnswer the question: {query}"
    print("Prompt", query)
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Use gpt-3.5-turbo if needed                                                                                                                             
        messages=[
            {"role": "system", "content": "You are an expert assistant providing information from the given context."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Main function to handle a query
def handle_query(query_json):
    query_data = json.loads(query_json)
    query = query_data["query"]
    
    # Generate query embedding
    query_embedding = generate_query_embedding(query)
    
    # Find relevant chunks
    relevant_chunks = find_relevant_chunks(query_embedding)
    
    # Generate a response
    response = generate_response(query, relevant_chunks)
    
    return response

# Example usage
if __name__ == "__main__":
    # Simulated JSON input
    query_json = json.dumps({"query": "What is the dealine for the course"})
    response = handle_query(query_json)
    # print("Response:", response)
