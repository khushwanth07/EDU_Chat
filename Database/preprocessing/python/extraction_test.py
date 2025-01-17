import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
API_KEY = os.getenv('API_KEY')

client = OpenAI(api_key=API_KEY)

DEVELOPER_PROMPT = """
You are a data analyst extracting information from an email history for the creation of a FAQ.
Keep the question and answer pairs as close to the original email as possible.
If there is no relevant question or no definite answer return an empty json object.
The questions and answers should be based solely on the email content and not contain any personal information.
There should be between 0 and 5 questions answers pairs in the json, prefer the minimum that covers the email content.
Output all questions and answers in english.
Each question should be followed by a single answer.
If the email does not contain a definite anwser set the answer to "NO ANSWER"
Don't forget to convert Unicode escape characters

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


# Function to read the email file
def read_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Get the email folder files list witch is a subfolder of the current directory
email_files = os.listdir("./Database/preprocessing/emails")
email_files.sort()

#print(email_files)  #Debugging for index error
email_index = 701

email = read_email(f"./Database/preprocessing/emails/{email_files[email_index]}")

print(f"Analyzing email {email_files[email_index]}")
#print(f"Email starts with sentence: {email[:50]}")

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "developer",
            "content": DEVELOPER_PROMPT,
        },
        {
            "role": "user",
            "content": email,
        }
    ]
)
response = json.loads(completion.choices[0].message.content)

# Print the full response for debugging
#print(completion)

# Pretty print the response
print(json.dumps(response, indent=4))
