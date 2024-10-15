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

    # Upload CSV or Excel file
    uploaded_file = st.file_uploader('Upload your CSV or Excel file', type=['csv', 'xlsx'])
    if uploaded_file is not None:
        try:
            # Check if the uploaded file is a CSV or an Excel file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                st.write("CSV file successfully uploaded.")
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
                st.write("Excel file successfully uploaded.")
            else:
                st.error("Unsupported file format. Please upload a CSV or Excel file.")

            st.dataframe(df)  # Display the uploaded data
            
            # Save file locally
            file_path = os.path.join("uploaded_files", uploaded_file.name)
            try:
                if not os.path.exists("uploaded_files"):
                    os.makedirs("uploaded_files")
            except Exception as e:
                st.error(f"Error creating directory: {e}")

            if uploaded_file.name.endswith('.csv'):
                df.to_csv(file_path, index=False)
            elif uploaded_file.name.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            
            # Commit and push to GitHub
            commit_message = st.text_input('Enter commit message', 'Add new file')
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
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a CSV or Excel file to proceed.")

if __name__ == '__main__':
    main()
