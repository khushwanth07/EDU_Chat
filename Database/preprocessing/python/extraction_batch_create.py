import json
import os

# Create the .temp folder if it does not exist
if not os.path.exists(".temp"):
    os.makedirs(".temp")

DEVELOPER_PROMPT = """
You are a data analyst tasked with extracting specific, case-based questions and answers from an email history to create a FAQ.
All Q&A pairs should be given in english. Do not use any other language.
Your goal is to identify and extract only those questions and answers that are explicitly stated in the email, retaining as much context and detail as possible.
Do not generalize, simplify, or extrapolate information beyond the given email content.
Ensure that all extracted Q&A pairs are specific to the described scenario and do not contain any personal information or assumptions.
If the email contains incomplete or ambiguous answers, clearly reflect this in the output by including "NO ANSWER" for the answer.
Questions and answers must remain true to the email's original content and preserve all essential information provided.
The output should contain between 0 and 5 Q&A pairs, focusing on the minimum required to fully capture the email's content without losing detail.
If no relevant question or definite answer exists in the email, return an empty JSON list.

This is an example of how the json should be structured and what good responses look like:
[
    {
        "Q": "What is the ECTS credit requirement for application to the MSc. AI in Society program at TUM?",
        "A": "The AI in Society program requires applicants to have at least 140 ECTS credits as a hard requirement."
    },
    {
        "Q": "Would being exmatriculated due to academic misconduct from a previous masters degree at a german university affect the application to the AI in Society program at TUM?",
        "A": "The first step is to check whether your previous degree and the MSc. AI in Society are similar. If they are not similar, you should be able to apply with no problems. If they are highly similar, you will likely be declined by TUM."
    },
    {
        "Q": "How should applicants with pre-diploma qualifications proceed when applying to the AI in Society program at TUM?",
        "A": "Applicants should ask their universities if they can issue the relevant ECTS or, if not possible, the respective SWS for their degree. If these documents can be obtained, they should be uploaded or sent to the admissions team."
    },
    {
        "Q": "How does the aptitude committee assess practical experience for the AI in Society program at TUM?",
        "A": "The aptitude committee decides if an applicant has suitable/sufficient practical experience. Applicants should submit evidence of their work, such as employment references."
    }
]

These are exmples of bad responses:
[
    {
        "Q": "What options are available for '\u00dcbertragungsweg der Rechnung'?",
        "A": "The options are Postweg, E-Mail (PDF), E-Mail (X-Rechnung), and PEPPOL."
    }, # Bad because the question is too specific and not relevant to the students.
    {
        "Q": "Wie kann man sich mit (Vor-)Diplom Abschl\u00fcssen im Portal bewerben, wenn es Schwierigkeiten gibt?",
        "A": "Es wird empfohlen, bei der Universit\u00e4t anzufragen, ob diese die ECTS oder, falls das nicht m\u00f6glich ist, die jeweiligen SWS ausstellen kann."
    }, # Bad because the question is in German.
    {
        "Q": "Could you provide me with an update on whether my application for the Master's degree in 'AI in Society' has been accepted?",
        "A": "We received your application and everything is fine."
    }, # Bad because the question is specific to the student and not relevant to the general public.
    {
        "Is it possible to speak with the heads of the masters program Ai in Society?",
        "answer": "Yes, you can reach out to the aptitude committee head, Prof. Dr. [REDACTED] at [REDACTED]@tum.de.",
    }, # Bad because the relevant information is redacted.
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
