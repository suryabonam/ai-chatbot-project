import mysql.connector
from mysql.connector import Error
import os

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        connection = mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", ""),
            database=os.environ.get("DB_NAME", "aquaculture_chatbot")
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def find_answer_in_knowledge_base(message):
    """Searches the knowledge_base table for a matching answer."""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        # ✅ ADD THIS (SMART MATCHING)

        cursor = connection.cursor(dictionary=True)

        # Convert user message to lowercase
        message = message.lower()

        # Get all questions from DB 
        cursor.execute("SELECT question, answer FROM knowledge_base")
        rows = cursor.fetchall()

        for row in rows:
            db_question = row["question"].lower()

            # Exact question matching
            if message == db_question:
                return row["answer"]

        return None
    except Error as e:
        print(f"Error searching knowledge base: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def save_message(user_message, bot_response):
    """Stores the user message and bot response in the messages table."""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = "INSERT INTO messages (user_message, bot_response) VALUES (%s, %s)"
        cursor.execute(query, (user_message, bot_response))
        connection.commit()
        return True
    except Error as e:
        print(f"Error saving message: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
