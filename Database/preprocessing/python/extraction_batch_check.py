"""
This script checks the responses from the batch extraction process, filters out the good responses,
and saves them to a JSON file. It also prints statistics about the responses.
"""

import json
import uuid
import os


def check_extraction_batch():
    """
    Check the responses from the batch extraction process and filter out the good responses.

    Returns:
    - dict: A dictionary of good responses with the following structure:
        {
            "uuid": {
                "created": 1737368942,
                "question": "Would it be possible to consider an exemption for a student who was unable to complete only one class due to external circumstances?",
                "answer": "In this situation, it is really only about formalities from our university and cannot be decided by an interview with our admission committee or similar.",
                "source_type": "email",
                "source": "email_001.txt",
                "request_id": "b1ae5c3c35ec86ea9c760955217a7ca9"
            },
            ...
        }
    """

    # Check that the extraction batch response file exists
    if not os.path.exists(".temp/extraction_batch_response.txt"):
        print("Extraction batch response file not found. First run the extraction batch download script.")
        return

    # Open the full response file
    with open(".temp/extraction_batch_response.txt", "r") as file:
        responses = file.readlines()

    # Initialize counters for different types of responses
    responses_with_empty_json = 0
    responses_with_invalid_json = 0
    responses_with_no_answer = 0
    responses_with_answer = 0

    # Initialize a dictionary to store the good responses
    good_responses = {}

    # Itterate over all responses
    for response in responses:

        # Load the response as a json object
        json_response = json.loads(response)

        # Check that there was no error
        if json_response["error"] is not None:
            print(f"Error in response {json_response['id']}: {json_response['error']}")
            continue

        # Check that the status code is 200
        if json_response["response"]["status_code"] != 200:
            print(f"Error in response {json_response['id']}: status code {json_response['response']['status_code']}")
            continue

        # Check that the response is not empty
        if json_response["response"]["body"]["choices"] == []:
            print(f"Error in response {json_response['id']}: empty response")
            continue

        # Check that the message content is not empty
        if json_response["response"]["body"]["choices"][0]["message"]["content"] == "":
            print(f"Error in response {json_response['id']}: empty message content")
            continue

        # Check if the message content is an empty list
        if json_response["response"]["body"]["choices"][0]["message"]["content"] == "[]\n":
            responses_with_empty_json += 1
            continue

        # Check if the message content is json parsable
        try:
            message = json.loads(json_response["response"]["body"]["choices"][0]["message"]["content"])
        except json.JSONDecodeError:
            print(f"Error in response {json_response['id']}: invalid json content")
            responses_with_invalid_json += 1
            continue

        # Check that the message content is a list of questions and answers
        if not isinstance(message, list):
            print(f"Error in response {json_response['id']}: message content is not a list")
            continue
        if not all(isinstance(item, dict) for item in message):
            print(f"Error in response {json_response['id']}: message content is not a list of dictionaries")
            continue
        if not all("Q" in item and "A" in item for item in message):
            print(f"Error in response {json_response['id']}: message content is not a list of questions and answers")
            continue

        # Check if there is an answer to the questions
        for item in message:
            if item["A"] == "NO ANSWER":
                responses_with_no_answer += 1
            else:
                responses_with_answer += 1

                # Create a dictionary for the good response
                item_dict = {
                    "created": json_response["response"]["body"]["created"],
                    "question": item["Q"],
                    "answer": item["A"],
                    "source_type": "email",
                    "source": json_response["custom_id"],
                    "request_id": json_response["response"]["request_id"],
                }

                # Add the good response to the dictionary
                good_responses[str(uuid.uuid4())] = item_dict

    # Print the statistics
    print(f"Responses with empty json: {responses_with_empty_json}")
    print(f"Responses with invalid json: {responses_with_invalid_json}")
    print(f"Responses with no answer: {responses_with_no_answer}")
    print(f"Responses with answer: {responses_with_answer}")

    # Write the data to a json file
    with open(".temp/extraction_batch_output.json", "w") as file:
        json.dump(good_responses, file, indent=4)


if __name__ == "__main__":
    check_extraction_batch()
