import psycopg2

conn = psycopg2.connect(database="alina_database",
                        host="localhost",
                        user="data_team",
                        password="7rt?!ERdyT6d$iTQR9E$",
                        port="5432")

cursor = conn.cursor()

cursor.execute("CREATE EXTENSION vector;")

cursor.execute("CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));")
cursor.execute("INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');")

cursor.execute("SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;")


# Fetch all results from the last query
results = cursor.fetchall()

# Print the results
for row in results:
    print(row)
    print(type(row))

# Close the cursor and connection
cursor.close()
conn.close()
