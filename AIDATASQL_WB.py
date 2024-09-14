#!/usr/bin/env python
# coding: utf-8

# In[3]:
import os
import streamlit as st
import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text
from github import Github, GithubException

# GitHub repository details - Ensure to set this as an environment variable
GITHUB_TOKEN = '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'  # Replace with your environment variable
GITHUB_REPO = 'AmmarJamshed/mysqlstreamlit'  # Only pass the 'owner/repository' format

# SQLite connection
DB_FILE = 'local_db.sqlite'

# Create SQLite engine
def create_sqlite_engine():
    engine = create_engine(f'sqlite:///{DB_FILE}')
    return engine

# Upload file to GitHub
def upload_to_github(file_path, commit_message):
    g = Github(GITHUB_TOKEN)
    try:
        st.write(f"Connecting to GitHub repository: {GITHUB_REPO}")
        repo = g.get_repo(GITHUB_REPO)
        st.write(f"Found repository: {repo.full_name}")
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as file:
            content = file.read()
        try:
            # Check if the file already exists
            contents = repo.get_contents(file_name)
            repo.update_file(contents.path, commit_message, content, contents.sha, branch='main')
            st.success(f"File {file_path} updated on GitHub successfully.")
        except GithubException as e:
            # If the file does not exist, create it
            if e.status == 404:
                repo.create_file(file_name, commit_message, content, branch='main')
                st.success(f"File {file_path} uploaded to GitHub successfully.")
            else:
                st.error(f"Error checking file existence on GitHub: {e.data['message']}")
                st.write(f"Exception details: {e}")
    except GithubException as e:
        st.error(f"Error accessing repository: {e.data['message']}")
        st.write(f"Repository Name: {GITHUB_REPO}")
        st.write(f"Exception: {e}")

# Function to upload DataFrame to SQLite
def upload_to_sqlite(df, table_name, engine):
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        st.success(f'Table {table_name} created successfully in SQLite.')
    except Exception as e:
        st.error(f'Error uploading to SQLite: {e}')

# Function to execute SQL query and return results or error
def execute_query(query, engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df, None
    except Exception as e:
        return None, str(e)

# Function to create a table
def create_table(query, engine):
    try:
        with engine.connect() as connection:
            connection.execute(text(query))
            st.success("Table created successfully.")
    except Exception as e:
        st.error(f"Error creating table: {e}")

# Function to rename a column using parameterized queries
def rename_column(table_name, old_column_name, new_column_name, engine):
    try:
        query = text('ALTER TABLE :table_name RENAME COLUMN :old_column_name TO :new_column_name')
        with engine.connect() as connection:
            connection.execute(query, {'table_name': table_name, 'old_column_name': old_column_name, 'new_column_name': new_column_name})
            st.success(f"Column '{old_column_name}' renamed to '{new_column_name}' successfully in table '{table_name}'.")
    except Exception as e:
        st.error(f"Error renaming column: {e}")

# Streamlit UI
def main():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://www.example.com/your-image.jpg");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title('Upload Data and Test SQL Queries on GitHub')

    # Upload CSV file
    uploaded_file = st.file_uploader('Upload your CSV file', type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df)
        
            # Save CSV file locally
            file_path = os.path.join("uploaded_files", uploaded_file.name)
            try:
                if not os.path.exists("uploaded_files"):
                    os.makedirs("uploaded_files")
            except Exception as e:
                st.error(f"Error creating directory: {e}")

            df.to_csv(file_path, index=False)
            
            # Commit and push to GitHub
            commit_message = st.text_input('Enter commit message', 'Add new CSV file')
            if st.button('Upload to GitHub'):
                upload_to_github(file_path, commit_message)
            
            # Get table name
            table_name = st.text_input('Enter table name to store data in SQLite')
            if st.button('Upload to SQLite'):
                if table_name:
                    engine = create_sqlite_engine()
                    upload_to_sqlite(df, table_name, engine)
                else:
                    st.error('Please enter a table name.')
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

    # Create Table
    st.header('Create Table in SQLite')
    create_table_query = st.text_area('Enter your CREATE TABLE SQL query')
    if st.button('Create Table'):
        if create_table_query.strip():
            engine = create_sqlite_engine()
            create_table(create_table_query, engine)
        else:
            st.error('Please enter a valid CREATE TABLE SQL query.')

    # Rename Column
    st.header('Rename Column in SQLite')
    rename_table_name = st.text_input('Enter table name for renaming column')
    old_column_name = st.text_input('Enter current column name')
    new_column_name = st.text_input('Enter new column name')
    if st.button('Rename Column'):
        if rename_table_name.strip() and old_column_name.strip() and new_column_name.strip():
            engine = create_sqlite_engine()
            rename_column(rename_table_name, old_column_name, new_column_name, engine)
        else:
            st.error('Please fill in all fields to rename the column.')

    # SQL Query testing
    st.header('Test SQL Queries')
    query = st.text_area('Enter your SQL query')
    if st.button('Execute Query'):
        if query.strip():
            engine = create_sqlite_engine()
            result, error = execute_query(query, engine)
            if error:
                st.error(f'Error: {error}')
            else:
                st.dataframe(result)
        else:
            st.error('Please enter a valid SQL query.')

if __name__ == '__main__':
    main()
