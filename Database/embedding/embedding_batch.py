import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from embedding_batch_create import create_embedding_batch
from embedding_batch_send import send_embedding_batch
from embedding_batch_status import status_embedding_batch
from embedding_batch_data import data_embedding_batch

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv("API_KEY")

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)


def main():
    # Create a batch of requests to get the embeddings for the questions extracted from the emails
    create_embedding_batch()

    print("Embedding batch created successfully.")

    # Send the batch of requests to the OpenAI API
    batch_id = send_embedding_batch(client)

    print("Embedding batch sent successfully.")

    output_file_id = None

    # Check the status of the batch processing
    while output_file_id is None:
        time.sleep(10)
        output_file_id = status_embedding_batch(batch_id, client)

    # Retrieve the batch output file and extract the embeddings
    data_embedding_batch(output_file_id, client)

    print("Embedding batch data retrieved successfully.")
    print("Done.")


if __name__ == "__main__":
    main()
