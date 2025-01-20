from database import find_closest_questions

if __name__ == "__main__":
    # Example of finding the closest questions to a given question
    question = "How much is the tuition fees?"

    # Find the closest questions to the given question
    entries = find_closest_questions(question, top_n=5)

    # Print the question that was given
    print(f"\nClosest questions to '{question}':")

    # Print the closest questions and their answers
    for entry in entries:
        print(f"Question: {entry['question_text']} with answer: {entry['answer_text']}")
