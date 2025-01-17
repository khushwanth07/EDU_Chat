from database import initialize_database, find_closest_questions

if __name__ == "__main__":

    initialize_database(clear=False)

    question = "How much is the tuition fees?"

    entries = find_closest_questions(question, top_n=4)

    print(f"\nClosest questions to '{question}':")
    for entry in entries:
        print(f"Question: {entry["question_text"]} with cosine distance: {entry["distance"]}")
