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
# Create SQLite engine
def create_sqlite_engine():
    engine = create_engine(f'sqlite:///{DB_FILE}')
    return engine

# Function to visualize the data
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

# Function to run SQL query and store results in session state
def run_query(engine, query):
    if "query_result" not in st.session_state:
        st.session_state["query_result"] = None
    try:
        result = pd.read_sql(query, engine)
        st.session_state["query_result"] = result
        return result
    except Exception as e:
        st.error(f"Failed to run query: {e}")
        return None

# Streamlit UI
def main():
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
            if not os.path.exists("uploaded_files"):
                os.makedirs("uploaded_files")
            df.to_csv(file_path, index=False)

            # Get table name
            table_name = st.text_input('Enter table name to store data in SQLite')
            if st.button('Upload to SQLite'):
                if table_name:
                    engine = create_sqlite_engine()
                    df.to_sql(table_name, engine, if_exists='replace', index=False)
                    st.success(f"Data successfully uploaded to table '{table_name}' in SQLite.")
                else:
                    st.error('Please enter a table name.')
            
            # SQL Query section
            engine = create_sqlite_engine()
            st.header("Run SQL Query")
            query = st.text_area("Enter your SQL query")
            if st.button("Run Query"):
                queried_data = run_query(engine, query)
                if queried_data is not None:
                    st.write("Query Result")
                    st.dataframe(queried_data)

                    # Visualize data if there are at least two columns
                    if len(queried_data.columns) >= 2:
                        visualize_data(queried_data)
                    else:
                        st.warning("At least two columns are required for visualization.")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a CSV or Excel file to proceed.")

if __name__ == '__main__':
    main()
