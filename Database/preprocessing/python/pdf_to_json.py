"""
This code is used to convert the extracted text from PDF files to JSON format.
It reads the pdf sections from the Database/preprocessing/pdf directory and creates a dictionary with the text,
source, and embedding.
The embeddings are created using the OpenAI API and stored in the dictionary.
"""

import json
import os
import uuid
import tqdm

from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# List all folders in the pdf directory
pdf_folders = os.listdir("Database/preprocessing/pdf")

entries = {}

for folder in pdf_folders:
    # List all files in the folder
    pdf_files = os.listdir(f"Database/preprocessing/pdf/{folder}")
    for file in pdf_files:
        # Open the file
        with open(f"Database/preprocessing/pdf/{folder}/{file}", "r", encoding='utf-8') as f:
            # print(f"Reading {file} in {folder}")
            # Read the file
            text = f.read()
            # Create a dictionary
            entry = {
                "pdf_text": text,
                "source": f"{folder}",
                "embedding": None,
            }
            # Append the dictionary to the entries list
            entries[str(uuid.uuid4())] = entry


for key, entry in tqdm.tqdm(entries.items(), desc="Creating embeddings", total=len(entries)):
    # Create an embedding for the text
    response = client.embeddings.create(
        input=entry["pdf_text"],
        model="text-embedding-3-small"
    )
    # Set the embedding in the dictionary
    entries[key]["embedding"] = response.data[0].embedding


with open(".temp/pdf.json", "w") as f:
    json.dump(entries, f, indent=4)
