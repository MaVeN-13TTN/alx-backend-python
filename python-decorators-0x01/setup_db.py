import sqlite3


# Create a simple users database for testing
def setup_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Create users table
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

    # Insert sample data
    cursor.execute("DELETE FROM users")  # Clear existing data

    sample_users = [
        ("Alice Johnson", "alice@example.com", 28),
        ("Bob Smith", "bob@example.com", 34),
        ("Charlie Brown", "charlie@example.com", 22),
        ("Diana Prince", "diana@example.com", 30),
    ]

    cursor.executemany(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)", sample_users
    )

    conn.commit()
    conn.close()
    print("Database setup complete!")


if __name__ == "__main__":
    setup_database()
