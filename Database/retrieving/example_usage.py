from database import find_closest_questions, find_closest_pdf, add_question

if __name__ == "__main__":
    # Example of finding the closest questions to a given question
    question = "What is the deadline for application to the program?"

    # Find the closest questions to the given question
    entries = find_closest_questions(question, top_n=5)

    # Print the question that was given
    print(f"\nClosest questions to '{question}':")

    # Print the closest questions and their answers
    for entry in entries:
        print(f"Question: {entry['question_text']}\nAnswer: {entry['answer_text']}\nDistance: {entry['distance']}")

    # Find the closest pdfs to the given question
    pdf = find_closest_pdf(question, top_n=5)

    # Print the closest pdfs
    print(f"\nClosest pdfs to '{question}':")
    for entry in pdf:
        print(f"PDF: {entry['pdf_text']}\nDistance: {entry['distance']}")

    # Create a new question answer pair
    new_question = "What is the deadline for application to the program?"
    new_answer = "The deadline for application is 31st of May."
    new_source = "AI_in_Society_MA_Studiengangsdokumentation_22072024.pdf"

    # Add the new question answer pair to the database
    add_question(new_question, new_answer, new_source)
