#!/usr/bin/env python
# coding: utf-8

# In[3]:

import streamlit as st
import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# MySQL connection parameters
MYSQL_HOST = 'localhost'  # Change to your MySQL host
MYSQL_USER = 'root'  # Change to your MySQL user
MYSQL_PASSWORD = 'Icedragon123'  # Change to your MySQL password
MYSQL_DB = 'Streamlit_dep'  # Change to your database name


# In[4]:


# Create a MySQL connection
def create_mysql_engine():
    engine = create_engine(f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}')
    return engine

# Function to upload DataFrame to MySQL
def upload_to_mysql(df, table_name, engine):
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        st.success(f'Table {table_name} created successfully in MySQL.')
    except SQLAlchemyError as e:
        st.error(f'Error uploading to MySQL: {e}')

# Function to execute SQL query and return results or error
def execute_query(query, engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
            return df, None
    except SQLAlchemyError as e:
        return None, str(e)


# In[5]:


# Streamlit UI
def main():
    st.title('Upload Data and Test SQL Queries in MySQL')

    # Upload CSV file
    uploaded_file = st.file_uploader('Upload your CSV file', type=['csv'])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)


# In[8]:


# Get table name
table_name = st.text_input('Enter table name to store data in MySQL')
if st.button('Upload to MySQL'):
    if table_name:
        engine = create_mysql_engine()
        upload_to_mysql(df, table_name, engine)
    else:
        st.error('Please enter a table name.')


# In[9]:


# SQL Query testing
st.header('Test SQL Queries')
query = st.text_area('Enter your SQL query')
if st.button('Execute Query'):
    engine = create_mysql_engine()
    result, error = execute_query(query, engine)
    if error:
        st.error(f'Error: {error}')
    else:
        st.dataframe(result)

if __name__ == '__main__':
    main()

