import os

from dotenv import load_dotenv
from openai import OpenAI

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Create a batch input file using the jsonl file
batch_input_file = client.files.create(
    file=open(".temp/batch_input.jsonl", "rb"),
    purpose="batch"
)

# Create a batch using the input file
batch_input_file_id = batch_input_file.id
batch = client.batches.create(
    input_file_id=batch_input_file_id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={
        "description": "email qna extraction",
    }
)

# Print the batch ID
print(batch.id)
