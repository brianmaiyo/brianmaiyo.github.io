import os
from flask import Flask, request, jsonify
import psycopg2
import pandas as pd
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from config.env file
load_dotenv('config.env')

# Retrieve database connection parameters from environment variables
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

# Function to establish a connection to the PostgreSQL database
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Function to create necessary tables in the database
def create_tables():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS summary (
                id SERIAL PRIMARY KEY
                -- Add more columns dynamically based on Excel file
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY
                -- Add more columns dynamically based on Excel file
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id SERIAL PRIMARY KEY
                -- Add more columns dynamically based on Excel file
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS week_check (
                id SERIAL PRIMARY KEY
                -- Add more columns dynamically based on Excel file
            )
        """)

        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print(f"Error creating tables: {e}")

# Route to read Excel data and insert into the database
@app.route('/api/import_excel', methods=['POST'])
def import_excel():
    try:
        file = request.files['file']
        if not file:
            return jsonify({'error': 'No file uploaded'}), 400

        # Read Excel file into pandas DataFrame
        df = pd.read_excel(file, sheet_name=None)

        # Insert data into database tables
        connection = get_db_connection()
        cursor = connection.cursor()

        for sheet_name, data in df.items():
            # Create table if it doesn't exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {sheet_name} (
                    id SERIAL PRIMARY KEY
                    -- Add more columns dynamically based on Excel file
                )
            """)
            
            # Insert data into the table
            data.to_sql(sheet_name, connection, if_exists='append', index=False)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Excel data imported successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    create_tables()  # Create tables when the application starts
    app.run(debug=True)
