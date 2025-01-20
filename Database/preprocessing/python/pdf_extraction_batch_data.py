import json
import uuid
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
file_response = client.files.content("file-AtpUNXmgEytqjDE1HK541J")
9
# Split the response into lines to get the individual responses for each email
responses = file_response.text.splitlines()

responses = [json.loads(response) for response in responses]

data = {}

for response in responses:

    # Get the created timestamp from the response
    created = response["response"]["body"]["created"]

    try:
        # Get the content of the response
        content = json.loads(response["response"]["body"]["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response: {response["response"]["body"]["choices"][0]["message"]["content"]}")
        continue

    for qa in content:
        # Create a unique key for the question answer pair
        key = str(uuid.uuid4())

        data[key] = {
            "created": created,  # timestamp of the api response
            "question": qa["Q"],  # question
            "answer": qa["A"],  # answer
            "source-type": "email",  # source type (email, pdf, etc.)
            "source": response["custom_id"],  # source email file (e.g. email_001.txt)
            "request_id": response["response"]["request_id"],  # request id of the api call
        }

# Print the data in a readable format
# print(json.dumps(data, indent=4))

# Save the data to a JSON file
with open(".temp/pdf_extraction_batch_output.json", "w") as file:
    json.dump(data, file, indent=4)
