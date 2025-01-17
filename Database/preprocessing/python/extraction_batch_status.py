import os

from dotenv import load_dotenv
from openai import OpenAI

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Retrieve the batch status
batch = client.batches.retrieve("batch_678a38f022b48190bf68b14a882080f5")

# Print the batch status
print(f"Batch status: {batch.status}")

# Print the batch id
print(f"Batch id: {batch.id}")

# Print the output file id
print(f"Output file id: {batch.output_file_id}")
