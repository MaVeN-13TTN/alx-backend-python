#!/usr/bin/python3
"""
Module for seeding a MySQL database with user data.
This module provides functions to connect to a MySQL database,
create a database and table, and insert data from a CSV file.
"""

import mysql.connector
import csv
import uuid
import os
from typing import Optional, Dict, List, Generator, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def connect_db() -> Optional[mysql.connector.connection.MySQLConnection]:
    """
    Connect to the MySQL database server.

    Returns:
        MySQLConnection: A connection to the MySQL server, or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "root"),
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL server: {err}")
        return None


def create_database(connection: mysql.connector.connection.MySQLConnection) -> bool:
    """
    Create the ALX_prodev database if it does not exist.

    Args:
        connection: A connection to the MySQL server.

    Returns:
        bool: True if database creation was successful, False otherwise.
    """
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        cursor.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error creating database: {err}")
        return False


def connect_to_prodev() -> Optional[mysql.connector.connection.MySQLConnection]:
    """
    Connect to the ALX_prodev database in MySQL.

    Returns:
        MySQLConnection: A connection to the ALX_prodev database, or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "root"),
            database=os.getenv("MYSQL_DATABASE", "ALX_prodev"),
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to ALX_prodev database: {err}")
        return None


def create_table(connection: mysql.connector.connection.MySQLConnection) -> bool:
    """
    Create a table user_data if it does not exist with the required fields.

    Args:
        connection: A connection to the ALX_prodev database.

    Returns:
        bool: True if table creation was successful, False otherwise.
    """
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX (user_id)
        )
        """
        )
        cursor.close()
        print("Table user_data created successfully")
        return True
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
        return False


def insert_data(
    connection: mysql.connector.connection.MySQLConnection, csv_file: str
) -> bool:
    """
    Insert data from a CSV file into the user_data table if it does not exist.

    Args:
        connection: A connection to the ALX_prodev database.
        csv_file: Path to the CSV file containing user data.

    Returns:
        bool: True if data insertion was successful, False otherwise.
    """
    try:
        # Check if file exists
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} does not exist")
            return False

        cursor = connection.cursor()

        # Read CSV file and insert data
        with open(csv_file, "r") as file:
            csv_reader = csv.reader(file)
            # Skip header row
            next(csv_reader)

            for row in csv_reader:
                # Generate a UUID for user_id
                user_id = str(uuid.uuid4())
                name = row[0]
                email = row[1]
                age = row[2]

                # Check if a record with the same email already exists
                cursor.execute(
                    "SELECT COUNT(*) FROM user_data WHERE email = %s", (email,)
                )
                count = cursor.fetchone()[0]

                if count == 0:
                    cursor.execute(
                        "INSERT INTO user_data (user_id, name, email, age) VALUES (%s, %s, %s, %s)",
                        (user_id, name, email, age),
                    )

        connection.commit()
        cursor.close()
        return True
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        return False
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return False


def get_rows(
    connection: mysql.connector.connection.MySQLConnection,
) -> Generator[Dict[str, Any], None, None]:
    """
    Generator function that streams rows from the user_data table one by one.

    Args:
        connection: A connection to the ALX_prodev database.

    Yields:
        Dict: A dictionary representing a row from the user_data table.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        for row in cursor:
            yield row

        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error fetching data: {err}")
        yield None


if __name__ == "__main__":
    # This block will be executed when the script is run directly
    connection = connect_db()
    if connection:
        create_database(connection)
        connection.close()

        connection = connect_to_prodev()
        if connection:
            create_table(connection)
            insert_data(connection, "user_data.csv")
            connection.close()
