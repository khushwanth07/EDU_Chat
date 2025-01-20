import os

from dotenv import load_dotenv
from openai import OpenAI


def status_embedding_batch(batch_id, client=None):
    """
    Check the status of the batch processing for the embedding of questions.
    Retrieve the batch_id from the embedding_batch_info.json file and check the status of the batch.

    Parameters:
    - client (OpenAI): The OpenAI client object.
    """
    if client is None:
        # Load the environment variables
        load_dotenv()

        # Get the API key from the environment variables
        API_KEY = os.getenv('API_KEY')

        # Create an OpenAI client with the API key
        client = OpenAI(api_key=API_KEY)

    # Retrieve the batch status
    batch = client.batches.retrieve(batch_id)

    completed = batch.request_counts.completed
    total = batch.request_counts.total
    failed = batch.request_counts.failed

    # Print the batch status
    print(f"Batch status: {batch.status}. {completed} out of {total} requests completed. {failed} requests failed.")

    # # Print the batch id
    # print(f"Batch id: {batch.id}")

    # # Print the output file id
    # print(f"Output file id: {batch.output_file_id}")

    if batch.status == "completed":
        return batch.output_file_id
    else:
        return None


if __name__ == "__main__":
    batch_id = ""

    status_embedding_batch(batch_id)
