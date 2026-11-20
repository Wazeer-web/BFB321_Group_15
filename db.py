
import os

import mysql.connector
from dotenv import load_dotenv

# Load database settings from the .env file
load_dotenv()


def get_db_connection():
    """Create and return a MySQL database connection."""

    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "kopano_inventory"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

    return connection
