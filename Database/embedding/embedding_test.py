"""
This script demonstrates how to create an embedding for a given input text using the OpenAI API.
"""

import os

from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Create an embedding for a given input text
response = client.embeddings.create(
    input="Where can the relevant admission criteria and procedures for the MSc. AI in Society program be found?",
    model="text-embedding-3-small"
)

# Print the embedding
print(response.data[0].embedding)
