import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=API_KEY)


DEVELOPER_PROMPT = """
You are a data analyst extracting information from text.
This data is used to generate FAQs and answers for a chatbot, for the website of the course program.
Keep the answers as authenticate as possible as there should be no to very less information loss.
The questions and answers should be based solely on the text content.

Provide clear Question and Answer pairs as JSON.
There should be between 20 and 50 questions and answers in the json, prefer the maximal that covers the text content
(especially every paragraph, you can create question for each paragraph and the answer should contain as more as possible the content of paragrah . 
You can give the quesion by the content 'Q:' and the relevant answer by the content 'A:').
.
This is an example of how the json should look like:
[
    {
        "Q": "What does the 'Law, Governance, and Regulation of Artificial Intelligence' course consists of?",
        "A": "The 'Law, Governance, and Regulation of Artificial Intelligence' course is a lecture scheduled for the first semester, with 3 hours per week. The course is worth 6 credits, and the examination is a written exam lasting 120 minutes. The course is taught in English."
    },
    {
        "Q": "What courses are offered in the elective area 'AI in Different Domains of Society'?",
        "A": "In the elective area 'AI in Different Domains of Society', students must earn at least 12 credits from the following courses: 'Learning Analytics', 'Gaze-based HCI', 'Responsible Data Science for Safe and Socially Aligned AI Applications', 'Advanced Topic: Law and Digitization in Action', 'Philosophy of Artificial Intelligence: Key Readings', 'Advanced Analysis of Variance Procedures', 'Development of Research Instruments'. All these courses are conducted in English."
    }
]
"""
'''
DEVELOPER_PROMPT = """
You are a data analyst tasked with extracting specific, case-based questions and answers from an email history to create a FAQ.
Your goal is to identify and extract only those questions and answers that are explicitly stated in the email, retaining as much context and detail as possible.
Do not generalize, simplify, or extrapolate information beyond the given email content.
Ensure that all extracted Q&A pairs are specific to the described scenario and do not contain any personal information or assumptions.
If the email contains incomplete or ambiguous answers, clearly reflect this in the output by including "NO ANSWER" for the answer.
Questions and answers must remain true to the email's original content and preserve all essential information provided.
The output should contain between 0 and 5 Q&A pairs, focusing on the minimum required to fully capture the email's content without losing detail.
If no relevant question or definite answer exists in the email, return an empty JSON object.

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
'''

# Function to read the email file
def read_email(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Get the email folder files list witch is a subfolder of the current directory
email_files = os.listdir("./Database/preprocessing/emails")
email_files.sort()

# print(email_files)  #Debugging for index error
email_index = 0

email = read_email(f"./Database/preprocessing/emails/{email_files[email_index]}")

print(f"Analyzing email {email_files[email_index]}")
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
            "content": email,
        },
    ],
    temperature = 0.2
)
response = json.loads(completion.choices[0].message.content)

# Print the full response for debugging
# print(completion)

# Pretty print the response
print(json.dumps(response, indent=4))
