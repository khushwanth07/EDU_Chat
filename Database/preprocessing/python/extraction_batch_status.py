"""
This script checks the status of the batch processing for the extraction of Q&A pairs.
It uses the OpenAI API and the batch_id to retrieve the status of the batch processing.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


def status_extraction_batch(batch_id, client=None):
    """
    Check the status of the batch processing for the extraction of Q&A pairs.
    Retrieve the batch_id from the extraction_batch_info.json file and check the status of the batch.

    Parameters:
    - batch_id (str): The ID of the batch to check.
    - client (OpenAI): The OpenAI client object.

    Returns:
    - bool: True if the batch processing is completed, False otherwise.
    """

    if not client:
        # Load the environment variables
        load_dotenv()

        # Get the API key from the environment variables
        API_KEY = os.getenv("API_KEY")

        # Create an OpenAI client with the API key
        client = OpenAI(api_key=API_KEY)

    # Retrieve the batch status
    batch = client.batches.retrieve(batch_id)

    # Check if the batch has completed
    if batch.status == "completed":
        print("Batch processing completed successfully.")

        with open(".temp/extraction_batch_final_status.txt", "w", encoding="utf-8") as file:
            file.write(str(batch))

        return batch.output_file_id
    else:
        completed = batch.request_counts.completed
        total = batch.request_counts.total
        failed = batch.request_counts.failed
        print(f"Current batch status: {batch.status}. Completed {completed} out of {total} requests. {failed} failed.")
        return None


if __name__ == "__main__":
    batch_id = ""

    status_extraction_batch(batch_id)
