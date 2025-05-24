import sqlite3


class DatabaseConnection:
    """
    A custom class-based context manager for handling database connections.

    This context manager automatically handles opening and closing database connections
    using the __enter__ and __exit__ methods, ensuring proper resource management.
    """

    def __init__(self, database_name="users.db"):
        """
        Initialize the DatabaseConnection context manager.

        Args:
            database_name (str): Name of the SQLite database file. Defaults to 'users.db'
        """
        self.database_name = database_name
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """
        Enter the context manager - open database connection.

        This method is called when entering the 'with' statement.
        It opens a connection to the database and returns the connection object.

        Returns:
            sqlite3.Connection: The database connection object
        """
        print(f"Opening database connection to {self.database_name}")
        self.connection = sqlite3.connect(self.database_name)
        self.cursor = self.connection.cursor()
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager - close database connection.

        This method is called when exiting the 'with' statement, even if an exception occurs.
        It ensures the database connection is properly closed.

        Args:
            exc_type: Exception type (if any exception occurred)
            exc_value: Exception value (if any exception occurred)
            traceback: Exception traceback (if any exception occurred)

        Returns:
            None: Returning None means exceptions will propagate normally
        """
        if self.connection:
            if exc_type is None:
                # No exception occurred, commit any pending transactions
                self.connection.commit()
                print("Database transaction committed successfully")
            else:
                # An exception occurred, rollback any pending transactions
                self.connection.rollback()
                print(f"Exception occurred: {exc_value}")
                print("Database transaction rolled back")

            # Always close the connection
            self.connection.close()
            print("Database connection closed")

        # Return None to propagate any exceptions that occurred
        return None


# Demonstration of using the context manager
if __name__ == "__main__":
    # First, let's ensure we have a users table with some data
    # This is just for demonstration - normally the database would already exist
    try:
        # Create and populate the database for testing
        with DatabaseConnection() as conn:
            cursor = conn.cursor()

            # Create table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    age INTEGER
                )
            """
            )

            # Check if table is empty and populate it
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]

            if count == 0:
                print("Populating database with sample data...")
                sample_users = [
                    ("Alice Johnson", "alice@example.com", 28),
                    ("Bob Smith", "bob@example.com", 34),
                    ("Charlie Brown", "charlie@example.com", 22),
                    ("Diana Prince", "diana@example.com", 30),
                ]

                cursor.executemany(
                    "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                    sample_users,
                )
                print("Sample data inserted successfully")

    except Exception as e:
        print(f"Error setting up database: {e}")

    print("\n" + "=" * 50)
    print("DEMONSTRATING CONTEXT MANAGER USAGE")
    print("=" * 50)

    # Use the context manager to perform a query
    try:
        with DatabaseConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()

            print(f"\nQuery Results - SELECT * FROM users:")
            print("-" * 40)

            if results:
                # Print header
                print(f"{'ID':<5} {'Name':<15} {'Email':<25} {'Age':<5}")
                print("-" * 40)

                # Print each user
                for user in results:
                    user_id, name, email, age = user
                    print(f"{user_id:<5} {name:<15} {email:<25} {age:<5}")
            else:
                print("No users found in the database")

            print(f"\nTotal users found: {len(results)}")

    except Exception as e:
        print(f"Error executing query: {e}")

    print("\nContext manager demonstration completed!")
