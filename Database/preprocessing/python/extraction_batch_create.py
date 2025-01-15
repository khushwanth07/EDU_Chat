import json
import os


DEVELOPER_PROMPT = """
You are a data analyst extracting information from an email history.
This data is used to generate FAQs and answers for a chatbot, for the website of the course program.
Keep the answers as authenticate as possible as there should be no to very less information loss.
The questions and answers should be based solely on the email content and not contain any personal information.
Anything containing personal information should be removed in such a way that the context of the message is not lost.
Provide clear Question and Answer pairs as JSON.
If there is no question or answer, please reply with an empty json object.
There should be between 0 and 5 questions and answers in the json, prefer the minimum that covers the email content.
Each question should be followed by a single answer.
This is an example of how the json should look like:
[
    {
        "Q": "What is the ECTS credit requirement for the MSc. AI in Society program at TUM?",
        "A": "The AI in Society program requires applicants to have at least 140 ECTS credits as a hard requirement."
    },
    {
        "Q": "What is the application deadline for the MSc. AI in Society program at TUM?",
        "A": "The application deadline for the MSc. AI in Society program at TUM is 31st May."
    }
]
"""


# Function to read a email file
def read_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Get a list of all email files
email_files = os.listdir("./Database/preprocessing/emails")[:3]

# Open the JSON file to write the batch requests
with open('.temp/batch_input.jsonl', 'w', encoding='utf-8') as json_file:
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
