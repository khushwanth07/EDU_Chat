import json

from database import insert_question


with open(".temp/embedding_batch_output.json") as file:
    embedding_data = json.load(file)

with open(".temp/extraction_batch_output.json") as file:
    extraction_data = json.load(file)

for key in extraction_data:
    question = extraction_data[key]["question"]
    answer = extraction_data[key]["answer"]
    source_type = extraction_data[key]["source_type"]
    source = extraction_data[key]["source"]
    embedding = embedding_data[key]["embedding"]
    insert_question(embedding, question, answer, source_type, source)
