import os
import json

from dotenv import load_dotenv
from openai import OpenAI


def status_extraction_batch(client=None):
    """
    Check the status of the batch processing for the extraction of Q&A pairs.
    Retrieve the batch_id from the extraction_batch_info.json file and check the status of the batch.

    Parameters:
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

    # Load the batch_id from the extraction_batch_info.json file
    with open(".temp/extraction_batch_info.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        batch_id = data["batch_id"]

    # Retrieve the batch status
    batch = client.batches.retrieve(batch_id)

    # Check if the batch has completed
    if batch.status == "completed":
        print("Batch processing completed successfully.")

        # Save the output_file_id to the extraction_batch_info.json file
        with open(".temp/extraction_batch_info.json", "r+", encoding="utf-8") as file:
            data = json.load(file)
            data["batch_output_file_id"] = batch.output_file_id
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

        with open(".temp/extraction_batch_final_status.txt", "w", encoding="utf-8") as file:
            file.write(str(batch))

        return True
    else:
        completed = batch.request_counts.completed
        total = batch.request_counts.total
        failed = batch.request_counts.failed
        print(f"Current batch status: {batch.status}. Completed {completed} out of {total} requests. {failed} failed.")
        return False


if __name__ == "__main__":
    status_extraction_batch()
