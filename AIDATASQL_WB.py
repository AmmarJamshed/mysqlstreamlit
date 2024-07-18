#!/usr/bin/env python
# coding: utf-8

# In[3]:

import streamlit as st
import pandas as pd
import sqlite3
import os
from sqlalchemy import create_engine
import github
from github import Github

# GitHub repository details
GITHUB_TOKEN = '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'  # Replace with your GitHub Personal Access Token
GITHUB_REPO = 'AmmarJamshed/Data-manip-with-Pandas-and-other-basic-libraires'  # Replace with your GitHub repo name

# SQLite connection
DB_FILE = 'local_db.sqlite'

# Create SQLite engine
def create_sqlite_engine():
    engine = create_engine(f'sqlite:///{DB_FILE}')
    return engine

# Upload file to GitHub
def upload_to_github(file_path, commit_message):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(GITHUB_REPO)
    with open(file_path, 'rb') as file:
        content = file.read()
    try:
        repo.create_file(file_path, commit_message, content, branch='main')
        st.success(f"File {file_path} uploaded to GitHub successfully.")
    except Exception as e:
        st.error(f"Error uploading to GitHub: {e}")

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
        result = engine.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df, None
    except Exception as e:
        return None, str(e)

# Streamlit UI
def main():
    st.title('Upload Data and Test SQL Queries on GitHub')

    # Upload CSV file
    uploaded_file = st.file_uploader('Upload your CSV file', type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)
        
        # Save CSV file locally
        file_path = os.path.join("uploaded_files", uploaded_file.name)
        if not os.path.exists("uploaded_files"):
            os.makedirs("uploaded_files")
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
