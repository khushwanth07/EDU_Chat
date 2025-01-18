'''
Install all the dependencies and give the datbase path, document path and run this file 
Later open the web/index.html and open the webpage from there.

'''
from flask import Flask, request, jsonify
import faiss
import numpy as np
import openai
import json
from flask_cors import CORS

# import numpy as np
# import openai
# import json
import pyaudio
import wave, os
import tempfile


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set your OpenAI API key
openai.api_key = "api-key"
# Load the FAISS index
VECTOR_DB_PATH = (r"C:\Users\khushwanth\Desktop\Project Week\Website\data.index")
index = faiss.read_index(VECTOR_DB_PATH)

# Load the text chunks for reference
with open("Website\documents.txt", "r") as file:
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


# Function to record audio and save to a file
def record_audio(file_path, duration=10):
    chunk = 1024  # 1 KB
    sample_format = pyaudio.paInt16  # 16-bit audio
    channels = 1  # Mono
    rate = 44100  # Sampling rate in Hz
    p = pyaudio.PyAudio()

    print("Recording...")
    stream = p.open(format=sample_format, channels=channels, rate=rate,
                    input=True, frames_per_buffer=chunk)

    frames = []
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    print("Recording finished.")

# Function to transcribe audio using OpenAI Whisper
def transcribe_audio(file_path):
    print("Transcribing audio...")
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript["text"]



# Function to generate a response
def generate_response(query, relevant_chunks):
    context = "\n".join([chunk[0] for chunk in relevant_chunks])
    prompt = f"Using the following context:\n{context}\n\nAnswer the question: {query}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert assistant providing information from the given context. Use a professional tone and ensure the response is concise, accurate, and aligned with the user's intent. Match the query to the most relevant knowledge source and prioritize clarity in the response.."},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

# API route to handle queries
@app.route('/query', methods=['POST'])
def handle_query():
    # Check if an audio file is present
    if 'audio' in request.files:
        audio_file = request.files['audio']
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            audio_file.save(temp_file.name)
            # Transcribe the audio using OpenAI Whisper
            spoken_text = transcribe_audio(temp_file.name)
            os.remove(temp_file.name)  # Clean up temporary file

        # Generate query embedding and response
        query = spoken_text
        query_embedding = generate_query_embedding(query)
        relevant_chunks = find_relevant_chunks(query_embedding)
        response = generate_response(query, relevant_chunks)
        return jsonify({"response": response})

    # Handle text-based queries (if any)
    query_data = request.json
    query = query_data.get("query", "")
    query_embedding = generate_query_embedding(query)
    relevant_chunks = find_relevant_chunks(query_embedding)
    response = generate_response(query, relevant_chunks)
    return jsonify({"response": response})


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
#     # Example usage
if __name__ == "__main__":
    # # Simulated JSON input
    # query_json = json.dumps({"query": "What is the dealine for the course"})
    # response = handle_query(query_json)
    # # print("Response:", response)
    app.run(host="0.0.0.0", port=5000, debug=True)

    temp_audio_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    try:
        # Record audio
        record_audio(temp_audio_file, duration=10)

        # Transcribe audio
        spoken_text = transcribe_audio(temp_audio_file)
        print(f"Transcribed Text: {spoken_text}")

        # Handle query
        if spoken_text:
            query_json = json.dumps({"query": spoken_text})
            response = handle_query(query_json)
            print("Response:", response)
    finally:
        # Clean up temporary audio file
        if os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
