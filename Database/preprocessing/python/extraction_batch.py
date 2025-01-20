import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from extraction_batch_create import create_extraction_batch
from extraction_batch_send import send_extraction_batch
from extraction_batch_status import status_extraction_batch
from extraction_batch_download import download_extraction_batch
from extraction_batch_check import check_extraction_batch


def main():
    # Load the environment variables
    load_dotenv()

    # Get the API key from the environment variables
    API_KEY = os.getenv("API_KEY")

    # Create an OpenAI client with the API key
    client = OpenAI(api_key=API_KEY)

    # Create a batch of requests to extract Q&A pairs from email content
    create_extraction_batch()

    print("Extraction batch created successfully.")

    # Send the batch of requests to the OpenAI API
    send_extraction_batch(client)

    print("Extraction batch sent successfully.")

    # Check the status of the batch processing
    while not status_extraction_batch(client):
        time.sleep(10)

    # Download the batch output file from the OpenAI API
    download_extraction_batch(client)

    print("Extraction batch downloaded successfully.")

    # Check the extraction batch for any errors and write the results to a JSON file
    check_extraction_batch()

    print("Extraction batch checked successfully.")
    print("Done.")


if __name__ == "__main__":
    main()
