import json
import uuid


"""
{
    "id": "batch_req_678e28721cec8190a98b5f0b3de7c4dd",
    "custom_id": "email_535.txt",
    "response": {
        "status_code": 200,
        "request_id": "95e81c87a17b9b6c06f2e74f18109155",
        "body": {
            "id": "chatcmpl-ArjQRmp7sQaiIgO3AQytjcz7BbVNh",
            "object": "chat.completion",
            "created": 1737369363,
            "model": "gpt-4-0613",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "[\n    {\n        \"Q\": \"Is it possible to submit the language certificate after the application deadline for the AI in Society Master's program?\",\n        \"A\": \"Only certain documents can be accepted after the application deadline, and unfortunately, the language certificate is not one of them.\"\n    },\n    {\n        \"Q\": \"Can English-taught modules with a total of at least 15 ECTS be considered as proof of language proficiency for the AI in Society Master's program?\",\n        \"A\": \"If you have completed English-taught modules with a total of at least 15 ECTS, these can also be considered as proof of language proficiency.\"\n    },\n    {\n        \"Q\": \"What qualifies as the practical part required for the application to the AI in Society Master's program?\",\n        \"A\": \"The practical part depends on what exactly you have done in your seminar papers. If no practical part in the form of data analyses or similar technical tools has been used and it is purely literature research, it unfortunately does not meet our requirements.\"\n    },\n    {\n        \"Q\": \"Can seminar papers be submitted as the practical part for the application to the AI in Society Master's program?\",\n        \"A\": \"NO ANSWER\"\n    }\n]",
                        "refusal": null
                    },
                    "logprobs": null,
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 1309,
                "completion_tokens": 257,
                "total_tokens": 1566,
                "prompt_tokens_details": {
                    "cached_tokens": 0,
                    "audio_tokens": 0
                },
                "completion_tokens_details": {
                    "reasoning_tokens": 0,
                    "audio_tokens": 0,
                    "accepted_prediction_tokens": 0,
                    "rejected_prediction_tokens": 0
                }
            },
            "service_tier": "default",
            "system_fingerprint": null
        }
    },
    "error": null
}
"""


def check_batch_extraction():
    # Open the full response file
    with open(".temp/extraction_batch_response.txt", "r") as file:
        responses = file.readlines()

    responses_with_empty_json = 0
    responses_with_invalid_json = 0
    responses_with_no_answer = 0
    responses_with_answer = 0

    good_responses = []

    # Go over all responses
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

                item_dict = {
                    "id": str(uuid.uuid4()),
                    "source_type": "email",
                    "source_id": json_response["custom_id"],
                    "created": json_response["response"]["body"]["created"],
                    "question": item["Q"],
                    "answer": item["A"],
                    "request_id": json_response["response"]["request_id"],
                }

                good_responses.append(item_dict)

    print(f"Responses with empty json: {responses_with_empty_json}")
    print(f"Responses with invalid json: {responses_with_invalid_json}")
    print(f"Responses with no answer: {responses_with_no_answer}")
    print(f"Responses with answer: {responses_with_answer}")

    return good_responses


if __name__ == "__main__":
    good_responses = check_batch_extraction()

    # Sort the data by the source_id
    good_responses = sorted(good_responses, key=lambda x: x["source_id"])

    # Write the data to a file
    with open(".temp/extraction_batch_data.json", "w") as file:
        json.dump(good_responses, file, indent=4)
