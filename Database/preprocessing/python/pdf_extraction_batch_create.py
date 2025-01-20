import json
import os

# Create the .temp folder if it does not exist
if not os.path.exists(".temp"):
    os.makedirs(".temp")

DEVELOPER_PROMPT = """
You are a data analyst extracting information from an pdf history.
This data is used to generate FAQs and answers for a chatbot, for the website of the course program.
Keep the answers as authenticate as possible as there should be no to very less information loss.
The questions and answers should be based solely on the text content.

Provide clear Question and Answer pairs as JSON.
There should be between 20 and 2000 questions and answers in the json, prefer the maximal that covers the text content
(especially every paragraph, you can create question for each paragraph and the answer should contain as more as possible the content of paragrah ).
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
def read_pdf(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Get a list of all email files
pdf_files = os.listdir("./Database/preprocessing/pdf")[3:5]

# Open the JSON file to write the batch requests
with open('.temp/pdf_extraction_batch_input.jsonl', 'w', encoding='utf-8') as json_file:
    # Loop through all email files
    for pdf_file in pdf_files:

        # Read the email content
        pdf_content = read_pdf(f"./Database/preprocessing/pdf/{pdf_file}")

        # Create the message for the OpenAI API
        messages = [
            {
                "role": "developer",
                "content": DEVELOPER_PROMPT,
            },
            {
                "role": "user",
                "content": pdf_content
            }
        ]

        # Create the batch request for the OpenAI API
        batch_request = {
            "custom_id": pdf_file,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4",
                "messages": messages,
                "max_tokens": 20000
            }
        }

        # Write the batch request to the JSON file
        json.dump(batch_request, json_file, ensure_ascii=False)

        # Add a new line to separate the requests
        json_file.write('\n')
