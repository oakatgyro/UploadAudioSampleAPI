import mysql.connector
from mysql.connector.connection import MySQLConnection
import os

host = os.environ.get("MYSQL_HOST")
port = os.environ.get("MYSQL_PORT", 3306)
db_name = os.environ.get("MYSQL_DATABASE")
user = os.environ.get("MYSQL_USER")
password = os.environ.get("MYSQL_PASSWORD")


async def get_db_connection() -> MySQLConnection:
    """get db connection for request

    Returns:
        MySQLConnection: mysql connection object
    """
    connection = mysql.connector.connect(
        host=host, port=port, user=user, password=password, database=db_name
    )
    try:
        yield connection
    finally:
        if connection:
            connection.close()
