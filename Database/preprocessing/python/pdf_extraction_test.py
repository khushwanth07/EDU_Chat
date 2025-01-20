import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI API key
API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=API_KEY)


DEVELOPER_PROMPT = """
You are a data analyst extracting information from a txt.
This data is used to generate FAQs.
Keep the answers as authenticate as possible as there should be no to very less information loss.
The questions and answers should be based solely on the text content.

Provide clear Question and Answer pairs as JSON.
There should be between 10 and 20 questions and answers in the json, prefer the maximal that covers the text content
(especially every paragraph, you can create question for each paragraph and the answer should contain as more as possible the content of paragrah . 
You can give the question by the content 'Q:' and the relevant answer by the content 'A:').

.
This is an example of how the json should look like:
[
    {
        "Q": "What is the aim of the 'Foundations of AI & Data Science' module?",
        "A": "The aim of the 'Foundations of AI & Data Science' under module code SOT86053 is to introduce foundational concepts and methodologies in AI and data science. It ensures that students gain a comprehensive understanding of the technical landscape of AI, preparing them to bridge practical requirements in AI applications."
    },
        "Q": "How does the 'Law, Governance and Regulation of Artificial Intelligence' module contribute to the qualification profile?",
        "A": "The module 'Law, Governance and Regulation of Artificial Intelligence' with module code SOT46302, provides insights into the legal, governance, and regulatory aspects of AI. It equips students with the skills and knowledge to navigate the complex legal landscape of AI. This knowledge fosters informed societal discussions and decisions, and promotes the ethical and responsible deployment of AI technologies."
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


#pdf = read_pdf(f"./Database/preprocessing/pdf/{pdf_files[pdf_index]}")
pdf = read_pdf(f"./Database/preprocessing/pdf/(studiengang)3.txt")

print(f"Analyzing pdf {pdf}")
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
