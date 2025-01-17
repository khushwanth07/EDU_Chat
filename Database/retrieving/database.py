import psycopg2

# Database connection details
db_config = {
    "database": "alina_database",
    "host": "localhost",
    "user": "data_team",
    "password": "7rt?!ERdyT6d$iTQR9E$",
    "port": "5432",
}


def get_connection():
    """
    Establish and return a database connection.

    Returns:
        psycopg2.extensions.connection: A connection to the PostgreSQL database.
    """
    return psycopg2.connect(**db_config)


def create_questions_table():
    """
    Create the questions table if it does not exist.

    Returns:
        None
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Check if the table already exists
        cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_name = 'questions'
        );
        """)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("Table 'questions' already exists.")
        else:
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
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


def clear_questions_table():
    """
    Clear the questions table.
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM questions;")
        connection.commit()
        print("Table 'questions' cleared successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


def insert_question(embedding, question_text, answer_text, source_type, source):
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
    connection = get_connection()
    try:
        cursor = connection.cursor()
        insert_query = """
        INSERT INTO questions (embedding, question_text, answer_text, source_type, source)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (embedding, question_text, answer_text, source_type, source))
        connection.commit()
        print("New question inserted successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


def find_closest_questions(embedding, top_n=5):
    """
    Find and return the top_n closest questions based on cosine similarity.

    Parameters:
        embedding (list[float]): The embedding vector to compare against.
        top_n (int): The number of closest entries to return.

    Returns:
        list[tuple]: A list of tuples containing the closest questions, each tuple with
                     (id, question_text, answer_text, source_type, source, similarity).
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        find_query = '''
        SELECT id, question_text, answer_text, source_type, source,
               1 - (embedding <-> %s) AS similarity
        FROM questions
        ORDER BY embedding <-> %s
        LIMIT %s;
        '''
        cursor.execute(find_query, (embedding, embedding, top_n))
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def print_database_info():
    """
    Print the list of databases and tables in the PostgreSQL server.

    Returns:
        None
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT datname FROM pg_database;")
        databases = cursor.fetchall()
        print("Databases:")
        for database in databases:
            print(database[0])

        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
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


def test_database():
    """
    Get the first question from the questions table and print it.
    Then find the closest questions to the same question.
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM questions LIMIT 1;")
        question = cursor.fetchone()
        print(f"Question of first question in 'questions' table: {question[2]}")
        print(f"Embedding of first question: {question[1]}")

        if question:
            embedding = question[1]
            closest_questions = find_closest_questions(embedding, top_n=5)
            print("\nClosest questions:")
            for q in closest_questions:
                print(q)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_questions_table()
    print_database_info()
    # Example usage
    # example_embedding = [0.1] * 1536  # Replace with real embedding values
    # insert_question(
    #     example_embedding, "What is AI?", "AI stands for Artificial Intelligence.", "pdf", "example_source.pdf"
    # )
    test_database()
