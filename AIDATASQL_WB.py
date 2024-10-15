#!/usr/bin/env python
# coding: utf-8

# In[3]:
import os
import pandas as pd
import streamlit as st
from github import Github, GithubException
from sqlalchemy import create_engine, text
import altair as alt

# GitHub repository details - Ensure to set this as an environment variable
GITHUB_TOKEN = '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'  # Replace with your environment variable
GITHUB_REPO = 'AmmarJamshed/Data-manip-with-Pandas-and-other-basic-libraires'  # Only pass the 'owner/repository' format

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

# Function to query data from SQLite
def query_sqlite(engine, query):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            data = result.fetchall()
            columns = result.keys()
            return pd.DataFrame(data, columns=columns)
    except Exception as e:
        st.error(f'Error executing query: {e}')
        return None

# Function to visualize queried data
def visualize_data(df):
    if df is not None and not df.empty:
        st.write("Visualization of Queried Data")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(df.columns[0], sort=None),
            y=alt.Y(df.columns[1])
        ).interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("No data available for visualization.")

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

    st.title('Upload Data, Query, and Visualize SQL Results')

    # Upload CSV file
    uploaded_file = st.file_uploader('Upload your CSV file', type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("File successfully uploaded.")
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
            
            # Advanced SQL Query section
            engine = create_sqlite_engine()
            st.header("Run SQL Query")
            query = st.text_area("Enter your SQL query")
            if st.button("Run Query"):
                queried_data = query_sqlite(engine, query)
                if queried_data is not None:
                    st.write("Query Result")
                    st.dataframe(queried_data)
                    
                    # Visualize data
                    if len(queried_data.columns) >= 2:  # Need at least two columns for visualization
                        visualize_data(queried_data)
                    else:
                        st.warning("At least two columns are required for visualization.")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
    else:
        st.info("Please upload a CSV file to proceed.")

if __name__ == '__main__':
    main()
