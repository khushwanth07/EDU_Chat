import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
API_KEY = os.getenv('API_KEY')

client = OpenAI(api_key=API_KEY)

DEVELOPER_PROMPT = """
You are a data analyst extracting information from an email history.
This data is used to generate a FAQ for the website of the course program.
Provide clear Question and Answer pairs as JSON.
The questions and answers should be based solely on the email content and not contain any personal information.
If there is no question or answer, please reply with an emppty json object.
There should be between 0 and 5 questions and answers in the json, prefer the minimum.
Each question should be followed by a sinlge answer.
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


# Function to read the email file
def read_email(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Get the email folder files list witch is a subfolder of the current directory
email_files = os.listdir("./Database/preprocessing/emails")

email = read_email(f"./Database/preprocessing/emails/{email_files[0]}")

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
# print(completion)

# Pretty print the response
print(json.dumps(response, indent=4))