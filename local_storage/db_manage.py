import sqlite3

DB_PATH = "local_storage/local_storage.db"

"""Create the 'state' table."""
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("""
        CREATE TABLE IF NOT EXISTS state (
            id INTEGER PRIMARY KEY,
            file_name TEXT,
            line_value TEXT,
            line_number INTEGER
        )
    """)
conn.commit()
conn.close()

def check_file_in_database(file_name):
    """Check if a log file is already in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM state WHERE file_name = ?
    """, (file_name,))
    result = cursor.fetchone()  # Fetches the count value
    conn.close()
    return result

def insert_state(file_name, line_value, line_number):
    """Insert a new state into the 'state' table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO state (file_name, line_value, line_number)
        VALUES (?, ?, ?)
    """, (file_name, line_value, line_number))
    conn.commit()
    conn.close()

def update_state(file_name, line_value, line_number):
    """Update an existing state in the 'state' table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE state
        SET line_value = ?,
            line_number = ?
        WHERE file_name = ?
    """, (line_value, line_number, file_name))
    conn.commit()
    conn.close()

def drop_table():
    """Drop the 'state' table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS state")
    conn.commit()
    conn.close()

# Example usage:
#insert_state("example.txt", "Lorem ipsum", 1)
#update_state("example.txt", "Updated line", 2)

