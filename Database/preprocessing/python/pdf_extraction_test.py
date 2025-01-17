import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=API_KEY)

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


# Function to read the email file
def read_pdf(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Get the email folder files list witch is a subfolder of the current directory
pdf_files = os.listdir("./Database/preprocessing/pdf")
pdf_files.sort()

# print(email_files)  #Debugging for index error
pdf_index = 5


pdf = read_pdf(f"./Database/preprocessing/pdf/{pdf_files[pdf_index]}")

print(f"Analyzing pdf {pdf_files[pdf_index]}")
# print(f"Email starts with sentence: {email[:50]}")

completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {
            "role": "developer",
            "content": DEVELOPER_PROMPT,
        },
        {
            "role": "user",
            "content": pdf,
        },
    ],
)
response = json.loads(completion.choices[0].message.content)

# Print the full response for debugging
# print(completion)

# Pretty print the response
print(json.dumps(response, indent=4))
