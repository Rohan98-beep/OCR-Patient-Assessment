import sqlite3

def run_query(database_path, query):
    """
    Runs a query on the specified SQLite database and prints the results.

    Args:
        database_path (str): Path to the SQLite database.
        query (str): SQL query to execute.
    """
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        print(f"Running query: {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        if results:
            for row in results:
                print(row)
        else:
            print("No results found.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Example usage
    database_path = "database/ocr_results.db"
    example_query = "SELECT * FROM ocr_results WHERE pain_level > 5;"
    run_query(database_path, example_query)
