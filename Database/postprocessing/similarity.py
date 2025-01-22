"""
This script processes embedding and extraction data to calculate cosine similarity between embeddings.
It identifies and prints pairs of questions with high similarity and visualizes the similarity matrix and histogram.
It can also be used to remove duplicate questions from the database.
"""

import json
import numpy as np
import matplotlib.pyplot as plt

# Load the embedding data
with open(".temp/embedding_batch_output.json") as file:
    embedding_data = json.load(file)

# Load the extraction data
with open(".temp/extraction_batch_output.json") as file:
    extraction_data = json.load(file)

embeddings = []
keys = []
for key in embedding_data:
    embeddings.append(embedding_data[key]["embedding"])
    keys.append(key)

# Convert to numpy array
embeddings = np.array(embeddings)

# Calculate norm of the embeddings
norm = np.linalg.norm(embeddings, axis=1)

# Calculate cosine similarity matrix
cosine_similarity = np.dot(embeddings, embeddings.T) / np.outer(norm, norm)

# Plot the cosine similarity matrix
plt.imshow(cosine_similarity, cmap="hot", interpolation="nearest")
plt.show()

# Plot the histogram of cosine similarity values
plt.hist(cosine_similarity.flatten(), bins=100)
plt.show()

# Set the threshold for cosine similarity
threshold = 0.99

for i in range(cosine_similarity.shape[0]):
    for j in range(cosine_similarity.shape[1]):
        if i != j and cosine_similarity[i, j] > threshold and i < j:
            print("Keys:", keys[i], "\n", keys[j])
            print("Similar pair of questions:")
            print("Question 1:", extraction_data[keys[i]]["question"])
            print("Question 2:", extraction_data[keys[j]]["question"])
            print("Cosine similarity:", cosine_similarity[i, j])
            # Delete one of the duplicate questions
#             try:
#                 embedding_data.pop(keys[j])
#                 extraction_data.pop(keys[j])
#             except KeyError:
#                 pass

# # Save the updated embedding data
# with open(".temp/embedding_batch_output.json", "w") as file:
#     json.dump(embedding_data, file)

# # Save the updated extraction data
# with open(".temp/extraction_batch_output.json", "w") as file:
#     json.dump(extraction_data, file)

pass
