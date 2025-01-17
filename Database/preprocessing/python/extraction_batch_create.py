import json
import os

# Create the .temp folder if it does not exist
if not os.path.exists(".temp"):
    os.makedirs(".temp")

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


# Function to read a email file
def read_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Get a list of all email files
email_files = os.listdir("./Database/preprocessing/emails")

# Sort the email files by name
email_files.sort()

# Only use the first 100 email files for debugging purposes
email_files = email_files[:100]

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
