from flask import Flask
import mysql.connector
import os
import time

app = Flask(__name__)

# UPDATED: Matches the environment keys and defaults in your docker-compose.yml
DB_HOST = os.environ.get("MYSQL_HOST", "mysql")
DB_USER = os.environ.get("MYSQL_USER", "root")
DB_PASSWORD = os.environ.get("MYSQL_PASSWORD", "root")
DB_NAME = os.environ.get("MYSQL_DB", "myapp")

def get_db_connection():
    """Attempts to connect to MySQL with a retry loop because MySQL takes time to boot up."""
    retries = 5
    while True:
        try:
            conn = mysql.connector.connect(
                host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
            )
            return conn
        except mysql.connector.Error as err:
            if retries == 0:
                raise err
            retries -= 1
            print("Database not ready yet. Retrying in 2 seconds...")
            time.sleep(2)

def init_db():
    """Creates a simple hits table if it doesn't exist yet."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS page_views (
            id INT AUTO_INCREMENT PRIMARY KEY,
            view_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/")
def hello():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO page_views () VALUES ()")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM page_views")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return f"<h1>Hello DevOps World!</h1><p>This page has been viewed {count} times.</p>"

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)