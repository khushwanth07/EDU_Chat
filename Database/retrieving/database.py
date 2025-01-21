import psycopg2
import json
import tqdm
import os

from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv("API_KEY")

# Create an OpenAI client with the API key
client = OpenAI(api_key=API_KEY)

# Database connection details
db_config = {
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT"),
}


def _get_connection():
    """
    Establish and return a database connection.

    Returns:
        psycopg2.extensions.connection: A connection to the PostgreSQL database.
    """
    return psycopg2.connect(**db_config)


def _create_questions_table():
    """
    Create the questions table if it does not exist.

    Returns:
        bool: True if the table was created, False if it already exists.
    """
    connection = _get_connection()
    try:
        print("Creating table 'questions'...")

        # Create a cursor object using the connection
        cursor = connection.cursor()

        # Create the extension for the vector data type
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Check if the questions table already exists
        cursor.execute(
            """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'questions'
        );
        """
        )
        table_exists = cursor.fetchone()[0]

        if table_exists:
            # Table already exists
            print("Table 'questions' already exists.")
            return False
        else:
            # Create the questions table with the required columns
            create_table_query = """
            CREATE TABLE IF NOT EXISTS questions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                embedding vector(1536),
                question_text TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                source_type VARCHAR(50),
                source VARCHAR(255)
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'questions' created successfully.")
            return True
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _create_pdf_table():
    """
    Create the questions table if it does not exist.

    Returns:
        bool: True if the table was created, False if it already exists.
    """
    connection = _get_connection()
    try:
        print("Creating table 'pdf'...")

        # Create a cursor object using the connection
        cursor = connection.cursor()

        # Create the extension for the vector data type
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Check if the questions table already exists
        cursor.execute(
            """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'pdf'
        );
        """
        )
        table_exists = cursor.fetchone()[0]

        if table_exists:
            # Table already exists
            print("Table 'pdf' already exists.")
            return False
        else:
            # Create the questions table with the required columns
            create_table_query = """
            CREATE TABLE IF NOT EXISTS pdf (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                embedding vector(1536),
                pdf_text TEXT NOT NULL,
                source_type VARCHAR(50),
                source VARCHAR(255)
            );
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'pdf' created successfully.")
            return True
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _clear_questions_table():
    """
    Clear the questions table.
    """
    connection = _get_connection()
    try:
        print("Clearing table 'questions'...")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM questions;")
        connection.commit()
        print("Table 'questions' cleared successfully.")
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _clear_pdf_table():
    """
    Clear the pdf table.
    """
    connection = _get_connection()
    try:
        print("Clearing table 'pdf'...")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM pdf;")
        connection.commit()
        print("Table 'pdf' cleared successfully.")
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _insert_question(embedding, question_text, answer_text, source_type, source):
    """
    Insert a new question into the questions table.

    Parameters:
        embedding (list[float]): The embedding vector representing the question.
        question_text (str): The text of the question.
        answer_text (str): The text of the answer.
        source_type (str): The type of the source (e.g., 'pdf', 'email').
        source (str): The specific source (e.g., filename).

    Returns:
        None
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO questions (embedding, question_text, answer_text, source_type, source)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (embedding, question_text, answer_text, source_type, source))
        connection.commit()
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _insert_pdf(embedding, pdf_text, source_type, source):
    """
    Insert a new pdf into the pdf table.

    Parameters:
        embedding (list[float]): The embedding vector representing the pdf.
        pdf_text (str): The text of the pdf.
        source_type (str): The type of the source (e.g., 'pdf', 'email').
        source (str): The specific source (e.g., filename).

    Returns:
        None
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO pdf (embedding, pdf_text, source_type, source)
        VALUES (%s, %s, %s, %s);
        """
        cursor.execute(insert_query, (embedding, pdf_text, source_type, source))
        connection.commit()
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _insert_questions_from_json():
    with open(".temp/embedding_batch_output.json") as file:
        embedding_data = json.load(file)

    with open(".temp/extraction_batch_output.json") as file:
        extraction_data = json.load(file)

    for key in tqdm.tqdm(extraction_data, desc="Loading questions from JSON"):
        question = extraction_data[key]["question"]
        answer = extraction_data[key]["answer"]
        source_type = extraction_data[key]["source_type"]
        source = extraction_data[key]["source"]
        embedding = embedding_data[key]["embedding"]
        _insert_question(embedding, question, answer, source_type, source)

    print("Questions inserted successfully.")


def _insert_pdf_from_json():
    with open(".temp/pdf.json") as file:
        pdf_data = json.load(file)

    for key in tqdm.tqdm(pdf_data, desc="Loading pdf from JSON"):
        pdf = pdf_data[key]["pdf_text"]
        source_type = "pdf"
        source = pdf_data[key]["source"]
        embedding = pdf_data[key]["embedding"]
        _insert_pdf(embedding, pdf, source_type, source)

    print("PDFs inserted successfully.")


def _create_index():
    """
    Create an index on the embedding column for faster similarity search.
    """
    connection = _get_connection()
    try:
        # Create a cursor object using the connection
        cursor = connection.cursor()
        # Check that the index does not already exist
        cursor.execute("SELECT EXISTS (SELECT FROM pg_indexes WHERE indexname = 'embedding_index');")
        index_exists = cursor.fetchone()[0]
        if index_exists:
            print("Index 'embedding_index' already exists.")
        else:
            # Create the embedding index for the questions table
            cursor.execute("CREATE INDEX embedding_index ON questions USING ivfflat(embedding);")
            connection.commit()
            # Create the embedding index for the pdf table
            cursor.execute("CREATE INDEX embedding_index ON pdf USING ivfflat(embedding);")
            connection.commit()
            print("Index created successfully.")
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _find_closest_question_embedding(embedding, top_n=5):
    """
    Find and return the top_n closest embeddings based on cosine similarity.

    Parameters:
        embedding (list[float]): The embedding vector to compare against.
        top_n (int): The number of closest entries to return.

    Returns:
        list[tuple]: A list of tuples containing the closest questions, each tuple with
                     (id, question_text, answer_text, source_type, source, distance).
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        find_query = """
        SELECT id, question_text,answer_text, source_type, source,
               (embedding <=> %s::vector) AS distance
        FROM questions
        ORDER BY distance ASC
        LIMIT %s;
        """
        cursor.execute(find_query, (embedding, top_n))
        results = cursor.fetchall()
        return results
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _find_closest_pdf_embedding(embedding, top_n=5):
    """
    Find and return the top_n closest embeddings based on cosine similarity.

    Parameters:
        embedding (list[float]): The embedding vector to compare against.
        top_n (int): The number of closest entries to return.

    Returns:
        list[tuple]: A list of tuples containing the closest pdf, each tuple with
                     (id, pdf_text, source_type, source, distance).
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        find_query = """
        SELECT id, pdf_text, source_type, source,
               (embedding <=> %s::vector) AS distance
        FROM pdf
        ORDER BY distance ASC
        LIMIT %s;
        """
        cursor.execute(find_query, (embedding, top_n))
        results = cursor.fetchall()
        return results
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _print_database_info():
    """
    Print the list of databases and tables in the PostgreSQL server.

    Returns:
        None
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT datname FROM pg_database;")
        databases = cursor.fetchall()
        print("Databases:")
        for database in databases:
            print(database[0])

        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print("\nTables in 'alina_database':")
        for table in tables:
            print(table[0])

        cursor.execute("SELECT COUNT(*) FROM questions;")
        question_count = cursor.fetchone()[0]
        print(f"\nNumber of questions in 'questions' table: {question_count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


def _get_number_of_questions():
    """
    Get the number of questions in the questions table.

    Returns:
        int: The number of questions in the questions table.
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM questions;")
        question_count = cursor.fetchone()[0]
        return question_count
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _get_number_of_pdf():
    """
    Get the number of pdf in the pdf table.

    Returns:
        int: The number of pdf in the pdf table.
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM pdf;")
        pdf_count = cursor.fetchone()[0]
        return pdf_count
    except Exception as e:
        raise e
    finally:
        cursor.close()
        connection.close()


def _test_database():
    """
    Get the first question from the questions table and print it.
    Then find the closest questions to the same question.
    """
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM questions LIMIT 1;")
        question = cursor.fetchone()
        print(f"Question of first question in 'questions' table: {question[2]}")
        print(f"Embedding of first question: {question[1]}")

        if question:
            embedding = question[1]
            closest_questions = _find_closest_question_embedding(embedding, top_n=4)
            print("\nClosest questions:")
            for q in closest_questions:
                print(q)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


def initialize_database(clear=False):
    """
    Initialize the database by creating the questions table and loading all questions from the JSON files.

    Parameters:
        clear (bool): Whether to clear the questions table if it allready exists.

    Returns:
        None
    """
    if _create_questions_table():
        _insert_questions_from_json()
        _create_index()

    elif clear:
        _clear_questions_table()
        _insert_questions_from_json()
        _create_index()

    print("Finished initializing questions database.")
    print(f"Loaded {_get_number_of_questions()} questions.")

    if _create_pdf_table():
        _insert_pdf_from_json()
        _create_index()

    elif clear:
        _clear_pdf_table()
        _insert_pdf_from_json()
        _create_index()

    print("Finished initializing pdf database.")
    print(f"Loaded {_get_number_of_pdf()} pdf.")


def embed_text(text):
    """
    Create an embedding for a given text.

    Parameters:
        text (str): The text to embed.

    Returns:
        list[float]: The embedding vector for the text.
    """
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    return response.data[0].embedding


def find_closest_questions(question, top_n=5):
    """
    Find the top_n closest questions to a given question text.

    Parameters:
        question (str): The text of the question to find similar questions for.
        top_n (int): The number of closest questions to return.

    Returns:
        list[dict]: A list of dictionaries containing the closest questions, each with
                    the keys 'id', 'question_text', 'answer_text', 'source_type', 'source', 'distance'.
    """
    embedding = embed_text(question)
    entries = _find_closest_question_embedding(embedding, top_n)
    entries = [
        {
            "id": entry[0],
            "question_text": entry[1],
            "answer_text": entry[2],
            "source_type": entry[3],
            "source": entry[4],
            "distance": entry[5],
        }
        for entry in entries
    ]
    return entries


def find_closest_pdf(pdf, top_n=5):
    """
    Find the top_n closest pdf to a given pdf text.

    Parameters:
        pdf (str): The text of the pdf to find similar pdf for.
        top_n (int): The number of closest pdf to return.

    Returns:
        list[dict]: A list of dictionaries containing the closest pdf, each with
                    the keys 'id', 'pdf_text', 'source_type', 'source', 'distance'.
    """
    embedding = embed_text(pdf)
    entries = _find_closest_pdf_embedding(embedding, top_n)
    entries = [
        {
            "id": entry[0],
            "pdf_text": entry[1],
            "source_type": entry[2],
            "source": entry[3],
            "distance": entry[4],
        }
        for entry in entries
    ]
    return entries


def add_question(question_text, answer_text, source, source_type="pdf"):
    """
    Add a new question to the questions table.

    Parameters:
        question_text (str): The text of the question.
        answer_text (str): The text of the answer.
        source (str): The specific source (e.g., filename).
        source_type (str): The type of the source (e.g., 'pdf', 'email').

    Returns:
        None
    """
    embedding = embed_text(question_text)
    _insert_question(embedding, question_text, answer_text, source_type, source)
    print("Question added successfully.")


if __name__ == "__main__":
    # Initialize the database
    # initialize_database(clear=False)
    pass
