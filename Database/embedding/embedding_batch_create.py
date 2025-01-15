import json

with open(".temp/batch_output.json", "r") as f:
    data = json.load(f)

with open(".temp/batch_input.jsonl", "w", encoding="utf-8") as json_file:
    for key in data:
        question = data[key]["question"]

        batch_request = {
            "custom_id": key,
            "method": "POST",
            "url": "/v1/embeddings",
            "body": {
                "model": "text-embedding-3-small",
                "input": question,
                "encoding_format": "float",
            }
        }

        # Write the batch request to the JSON file
        json.dump(batch_request, json_file, ensure_ascii=False)

        # Add a new line to separate the requests
        json_file.write('\n')
