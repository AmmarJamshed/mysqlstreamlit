#!/usr/bin/env python
# coding: utf-8

# In[3]:

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
# visual function
def visualize_data(df):
    try:
        st.subheader("Visualize Data")
        
        # Use session state to store selected columns for the X and Y axes
        if "x_axis" not in st.session_state:
            st.session_state["x_axis"] = df.columns[0]
        if "y_axis" not in st.session_state:
            st.session_state["y_axis"] = df.columns[1]

        # Let the user select columns for X and Y axes using session state
        x_axis = st.selectbox("Select the X-axis column", df.columns, index=df.columns.get_loc(st.session_state["x_axis"]), key="x_axis")
        y_axis = st.selectbox("Select the Y-axis column", df.columns, index=df.columns.get_loc(st.session_state["y_axis"]), key="y_axis")
        
        # Create Altair chart
        chart = alt.Chart(df).mark_line().encode(
            x=x_axis,
            y=y_axis
        ).properties(
            width=700,
            height=400
        )
        
        st.altair_chart(chart)

    except Exception as e:
        st.error(f"Failed to visualize data: {e}")
# query function
def query_sqlite(engine, query):
    try:
        # Connect to the SQLite database and execute the query
        with engine.connect() as connection:
            result = connection.execute(text(query))
            # Fetch all results and convert to DataFrame
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df
    except Exception as e:
        st.error(f"Failed to execute query: {e}")
        return None
# function to upload data to sql
def upload_to_sqlite(df, table_name, engine):
    try:
        # Upload the dataframe to the SQLite database
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        st.success(f"Data uploaded successfully to the '{table_name}' table in SQLite.")
    except Exception as e:
        st.error(f"Failed to upload data to SQLite: {e}")

# Function to upload file to GitHub
def upload_to_github(file_path, commit_message):
    try:
        # Initialize GitHub object with token
        g = Github(GITHUB_TOKEN)

        # Get the GitHub repository
        repo = g.get_repo(GITHUB_REPO)

        # Read the file content
        with open(file_path, "rb") as file:
            content = file.read()

        # Determine file name from path
        file_name = os.path.basename(file_path)

        # Check if the file already exists in the repository
        try:
            existing_file = repo.get_contents(f"uploaded_files/{file_name}")
            # If the file exists, update it
            repo.update_file(existing_file.path, commit_message, content, existing_file.sha)
            st.success(f"File '{file_name}' updated in the repository.")
        except GithubException:
            # If the file does not exist, create a new one
            repo.create_file(f"uploaded_files/{file_name}", commit_message, content)
            st.success(f"File '{file_name}' uploaded to the repository.")

    except GithubException as e:
        st.error(f"Failed to upload file to GitHub: {e}")
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
                # Read Excel file using pandas
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

            # Save file based on extension
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
