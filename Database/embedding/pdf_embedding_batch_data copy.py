import json
import os

from dotenv import load_dotenv
from openai import OpenAI

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv("API_KEY")

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Get the file response from the OpenAI API
file_response = client.files.content("file-KWRe4pbEcmiub7sxnVWvca")

# Split the response into lines to get the individual responses for each email
responses = file_response.text.splitlines()

responses = [json.loads(response) for response in responses]

data = {}

for response in responses:
    # Create a unique key for the question answer pair
    key = response["custom_id"]

    # Get the embedding from the response
    embedding = response["response"]["body"]["data"][0]["embedding"]

    # Get the request id from the response
    request_id = response["id"]

    data[key] = {
        "embedding": embedding,  # embedding of the response
        "request_id": request_id,  # request id of the api call
    }

# Print the data in a readable format
# print(json.dumps(data, indent=4))

# Save the data to a JSON file
with open(".temp/pdf_embedding_batch_output.json", "w") as file:
    json.dump(data, file, indent=4)
