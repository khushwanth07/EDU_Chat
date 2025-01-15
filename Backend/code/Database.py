import os
import faiss
import numpy as np
import openai
import pdfplumber
import tiktoken

# Set your OpenAI API key
openai.api_key = "api-key"

# Directory containing PDF files
PDF_DIRECTORY = (r"C:\Users\khushwanth\Desktop\Project Week\pdf_data")
VECTOR_DB_PATH = (r"C:\Users\khushwanth\Desktop\Project Week\data.index")

# Tokenizer instance for the embedding model
tokenizer = tiktoken.encoding_for_model("text-embedding-ada-002")

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to split text into chunks within a token limit
def split_text_into_chunks(text, max_tokens=500):
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph_tokens = len(tokenizer.encode(paragraph))
        current_chunk_tokens = len(tokenizer.encode(current_chunk))
        
        if current_chunk_tokens + paragraph_tokens <= max_tokens:
            current_chunk += paragraph + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Function to generate embeddings for text chunks
def generate_embeddings(text_chunks):
    embeddings = []
    for chunk in text_chunks:
        response = openai.Embedding.create(
            input=chunk,
            model="text-embedding-ada-002"
        )
        embedding = response["data"][0]["embedding"]
        embeddings.append(embedding)
    return np.array(embeddings, dtype='float32')

# Main function to create a vector database
def create_vector_database(pdf_directory, vector_db_path):
    all_chunks = []
    all_texts = []
    
    # Extract and process text from each PDF
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            print(f"Processing {filename}...")
            text = extract_text_from_pdf(pdf_path)
            chunks = split_text_into_chunks(text)
            all_chunks.extend(chunks)
            all_texts.extend(chunks)
    
    # Generate embeddings for all text chunks
    print("Generating embeddings...")
    embeddings = generate_embeddings(all_chunks)

    # Create and populate a FAISS index
    print("Creating vector database...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save the index
    faiss.write_index(index, vector_db_path)
    print(f"Vector database saved to {vector_db_path}")
    
    # Save associated text data for reference
    with open("documents.txt", "w") as file:
        file.writelines(chunk + "\n---\n" for chunk in all_texts)
    print("Associated text saved to documents.txt")

# Run the script
if __name__ == "__main__":
    create_vector_database(PDF_DIRECTORY, VECTOR_DB_PATH)
