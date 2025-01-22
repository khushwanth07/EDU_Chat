import os
import time
import random

from dotenv import load_dotenv
from openai import OpenAI

<<<<<<< HEAD
from extraction_batch_create import create_extraction_batch
from extraction_batch_send import send_extraction_batch
from extraction_batch_status import status_extraction_batch
from extraction_batch_download import download_extraction_batch
from extraction_batch_check import check_extraction_batch
=======
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

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Create the .temp folder if it does not exist
if not os.path.exists(".temp"):
    os.makedirs(".temp")
>>>>>>> origin/Final-Touches


def main():
    # Load the environment variables
    load_dotenv()

    # Get the API key from the environment variables
    API_KEY = os.getenv("API_KEY")

    # Create an OpenAI client with the API key
    client = OpenAI(api_key=API_KEY)

    # Create a batch of requests to extract Q&A pairs from email content
    create_extraction_batch(number_of_emails=10)

    print("Extraction batch created successfully.")

    # Send the batch of requests to the OpenAI API
    batch_id = send_extraction_batch(client)

    print("Extraction batch sent successfully.")

    output_file_id = None

    # Check the status of the batch processing
    while output_file_id is None:
        time.sleep(10)
        output_file_id = status_extraction_batch(batch_id, client)

    # Download the batch output file from the OpenAI API
    download_extraction_batch(output_file_id, client)

    print("Extraction batch downloaded successfully.")

    # Check the extraction batch for any errors and write the results to a JSON file
    check_extraction_batch()

    print("Extraction batch checked successfully.")
    print("Done.")


<<<<<<< HEAD
if __name__ == "__main__":
    main()
=======
def extraction_batch_create():
    # Get a list of all email files
    email_files = os.listdir("./Database/preprocessing/emails")

    # Sort the email files by name
    email_files.sort()

    # Shuffle the email files for randomness
    # random.shuffle(email_files)

    # Only use the first x email files for debugging purposes
    # email_files = email_files[:10]

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
                    "temperature": 0.2,
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
        try:
            content = json.loads(response["response"]["body"]["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"Error: {e}")
            print(f"Response: {response}")
            content = []

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
>>>>>>> origin/Final-Touches
