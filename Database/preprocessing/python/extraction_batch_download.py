"""
This script downloads the batch output file from the OpenAI API.
The result is written to a text file in the .temp folder.
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


def download_extraction_batch(batch_output_file_id, client=None):
    """
    Download the batch output file from the OpenAI API.
    Retrieve the batch_output_file_id from the extraction_batch_info.json file and download the file.

    Parameters:
    - batch_output_file_id (str): The ID of the batch output file.
    - client (OpenAI): The OpenAI client object.
    """

    if not client:
        # Load the environment variables
        load_dotenv()

        # Get the API key from the environment variables
        API_KEY = os.getenv("API_KEY")

        # Create an OpenAI client with the API key
        client = OpenAI(api_key=API_KEY)

    # Get the file response from the OpenAI API
    file_response = client.files.content(batch_output_file_id)

    # Save the file response to a text file
    with open(".temp/extraction_batch_response.txt", "w") as file:
        file.write(file_response.text)


if __name__ == "__main__":
    batch_output_file_id = ""

    download_extraction_batch(batch_output_file_id)
