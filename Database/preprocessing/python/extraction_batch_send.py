import os
import json

from dotenv import load_dotenv
from openai import OpenAI


def send_extraction_batch(client=None):
    """
    Send a batch of requests to extract Q&A pairs from email content using the OpenAI API.
    Read the batch input file and create a batch using the input file.
    Save the batch_id and batch_input_file_id to the extraction_batch_info.json file.

    Parameters:
    - client (OpenAI): The OpenAI client object.
    """

    if not client:
        # Load the environment variables
        load_dotenv()

        # Get the API key from the environment variables
        API_KEY = os.getenv("API_KEY")

        # Create an OpenAI client with the API key
        client = OpenAI(api_key=API_KEY)

    # Check that the input file exists
    if not os.path.exists(".temp/extraction_batch_input.jsonl"):
        raise FileNotFoundError(
            "The batch input file does not exist. Create it first using extraction_batch_create.py."
        )

    # Create a batch input file using the JSONL file
    batch_input_file = client.files.create(file=open(".temp/extraction_batch_input.jsonl", "rb"), purpose="batch")

    # Create a batch using the input file
    batch_input_file_id = batch_input_file.id
    batch = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": "Batch of emails for the extraction of QnA pairs."},
    )

    # Save the batch_id and batch_input_file_id to the extraction_batch_info.json file
    with open(".temp/extraction_batch_info.json", "r+", encoding="utf-8") as file:
        data = json.load(file)
        data["batch_input_file_id"] = batch_input_file_id
        data["batch_id"] = batch.id
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

    # Print the batch_id and batch_input_file_id
    print(f"Batch ID: {batch.id}")
    print(f"Batch Input File ID: {batch_input_file_id}")


if __name__ == "__main__":
    send_extraction_batch()
