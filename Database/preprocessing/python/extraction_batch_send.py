import os

from dotenv import load_dotenv
from openai import OpenAI

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Check that the input file exists
if not os.path.exists(".temp/extraction_batch_input.jsonl"):
    raise FileNotFoundError("The batch input file does not exist. Create it first using extraction_batch_create.py.")

# Create a batch input file using the jsonl file
batch_input_file = client.files.create(
    file=open(".temp/extraction_batch_input.jsonl", "rb"),
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
