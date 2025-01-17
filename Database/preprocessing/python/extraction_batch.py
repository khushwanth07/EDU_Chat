import json
import os
import uuid
import time

from dotenv import load_dotenv
from openai import OpenAI

DEVELOPER_PROMPT = """
You are a data analyst extracting information from an email history for the creation of a FAQ.
Keep the question and answer pairs as close to the original email as possible.
If there is no relevant question or no definite answer return an empty json object.
The questions and answers should be based solely on the email content and not contain any personal information.
There should be between 0 and 5 questions answers pairs in the json, prefer the minimum that covers the email content.
Output all questions and answers in english.
Each question should be followed by a single answer.
If the email does not contain a definite anwser set the answer to "NO ANSWER"

This is an example of how the json should be structured:
[
    {
        "Q": "What is the ECTS credit requirement for the MSc. AI in Society program at TUM?",
        "A": "The AI in Society program requires applicants to have at least 140 ECTS credits as a hard requirement."
    },
    {
        "Q": "What is the application deadline for the MSc. AI in Society program at TUM?",
        "A": "NO ANSWER"
    }
]
"""

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Create the .temp folder if it does not exist
if not os.path.exists(".temp"):
    os.makedirs(".temp")


# Function to read a email file
def read_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def extraction_batch_create():
    # Get a list of all email files
    email_files = os.listdir("./Database/preprocessing/emails")

    # Sort the email files by name
    email_files.sort()

    # Only use the first x email files for debugging purposes
    email_files = email_files[:5]

    # Open the JSON file to write the batch requests
    with open('.temp/extraction_batch_input.jsonl', 'w', encoding='utf-8') as json_file:
        # Loop through all email files
        for email_file in email_files:

            # Read the email content
            email_content = read_email(f"./Database/preprocessing/emails/{email_file}")

            # Create the message for the OpenAI API
            messages = [
                {
                    "role": "developer",
                    "content": DEVELOPER_PROMPT,
                },
                {
                    "role": "user",
                    "content": email_content
                }
            ]

            # Create the batch request for the OpenAI API
            batch_request = {
                "custom_id": email_file,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4",
                    "messages": messages,
                    "max_tokens": 2000
                }
            }

            # Write the batch request to the JSON file
            json.dump(batch_request, json_file, ensure_ascii=False)

            # Add a new line to separate the requests
            json_file.write('\n')


def extraction_batch_send():
    # Check that the input file exists
    if not os.path.exists(".temp/extraction_batch_input.jsonl"):
        raise FileNotFoundError("The batch input file does not exist.")

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

    return batch.id


def extraction_batch_status(batch_id):
    # Retrieve the batch status
    batch = client.batches.retrieve(batch_id)

    # Get the progress of the batch
    progress = [batch.request_counts.completed, batch.request_counts.total]

    return batch.status, batch.output_file_id, progress


def extraction_batch_data(output_file_id):
    # Get the file response from the OpenAI API
    file_response = client.files.content(output_file_id)

    # Split the response into lines to get the individual responses for each email
    responses = file_response.text.splitlines()

    responses = [json.loads(response) for response in responses]

    data = {}

    for response in responses:
        # Create a unique key for the question answer pair
        key = str(uuid.uuid4())

        # Get the created timestamp from the response
        created = response["response"]["body"]["created"]

        # Get the content of the response
        content = json.loads(response["response"]["body"]["choices"][0]["message"]["content"])

        for qa in content:
            data[key] = {
                "created": created,  # timestamp of the api response
                "question": qa["Q"],  # question
                "answer": qa["A"],  # answer
                "source_type": "email",  # source type (email, pdf, etc.)
                "source": response["custom_id"],  # source email file (e.g. email_001.txt)
                "request_id": response["response"]["request_id"],  # request id of the api call
            }
            if qa["A"] == "NO ANSWER":
                data[key]["source_type"] = "no_answer"

    # Print the data in a readable format
    # print(json.dumps(data, indent=4))

    # Save the data to a JSON file
    with open(".temp/extraction_batch_output.json", "w") as file:
        json.dump(data, file, indent=4)


if __name__ == '__main__':
    print("Creating extraction batch...")
    extraction_batch_create()
    print("Sending extraction batch...")
    batch_id = extraction_batch_send()
    print(f"Batch running with ID: \"{batch_id}\"")
    status, output_file_id, progress = extraction_batch_status(batch_id)
    while status != "completed":
        print(f"Batch status: {status}. Progress: {progress[0]}/{progress[1]}")
        time.sleep(5)
        status, output_file_id, progress = extraction_batch_status(batch_id)
    print("Batch completed. Retrieving data...")
    extraction_batch_data(output_file_id)
    print("Batch complete.")
