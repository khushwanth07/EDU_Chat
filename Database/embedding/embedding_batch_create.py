"""
This script creates a batch of requests to get the embeddings for the questions extracted from the emails.
Read the questions from the extraction_batch_output.json file and create a batch request for each question.
The batch requests are written to a JSONL file for batch processing.
"""

import json
import os


def create_embedding_batch():
    """
    Create a batch of requests to get the embeddings for the questions extracted from the emails.
    Read the questions from the extraction_batch_output.json file and create a batch request for each question.
    """
    # Create the .temp folder if it does not exist
    if not os.path.exists(".temp"):
        os.makedirs(".temp")

    with open(".temp/extraction_batch_output.json", "r") as f:
        data = json.load(f)

    # Open the JSON file to write the batch requests
    with open(".temp/embedding_batch_input.jsonl", "w", encoding="utf-8") as json_file:
        # Loop through all the questions
        for key in data:
            question = data[key]["question"]

            batch_request = {
                "custom_id": key,  # Use the uuid of the question as the custom_id
                "method": "POST",
                "url": "/v1/embeddings",
                "body": {
                    "model": "text-embedding-3-small",  # Use the text-embedding-3-small model
                    "input": question,  # The question to get the embedding for
                    "encoding_format": "float",
                }
            }

            # Write the batch request to the JSON file
            json.dump(batch_request, json_file, ensure_ascii=False)

            # Add a new line to separate the requests
            json_file.write('\n')


if __name__ == "__main__":
    create_embedding_batch()
