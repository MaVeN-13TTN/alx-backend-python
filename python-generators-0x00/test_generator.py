#!/usr/bin/python3
"""
Test script to demonstrate the generator functionality.
"""

import seed

def main():
    """
    Main function to test the generator functionality.
    """
    # Connect to the database
    connection = seed.connect_to_prodev()
    
    if connection:
        print("Connected to ALX_prodev database")
        
        # Use the generator to stream rows
        print("\nStreaming rows from the database using generator:")
        row_generator = seed.get_rows(connection)
        
        # Print the first 5 rows
        for i, row in enumerate(row_generator):
            if i >= 5:
                break
            print(f"Row {i+1}: {row}")
        
        # Close the connection
        connection.close()
        print("\nConnection closed")
    else:
        print("Failed to connect to the database")

if __name__ == "__main__":
    main()
