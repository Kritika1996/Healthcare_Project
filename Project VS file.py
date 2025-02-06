# Importing Libraries
import pandas as pd
import numpy as np
import mysql.connector
import os
import streamlit as st
import sqlalchemy
from sqlalchemy import create_engine
from urllib.parse import quote
from sqlalchemy import create_engine

Healthcare_data = pd.read_excel(r"C:\Users\varun\OneDrive\Documents\Healthcare project VS\Healtcare-Dataset.xlsx")

Healthcare_data.info()

Healthcare_data.isnull().sum()

Healthcare_data.dropna(subset = ['Followup Date'], inplace = True)

Healthcare_data.head()

Healthcare_data = Healthcare_data.rename(columns={'Followup Date': 'Followup_Date','Billing Amount':'Billing_Amount','Health Insurance Amount':'Health_Insurance_Amount'})


# creating sql connection
mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Root@123",
    autocommit = True)

# creating cursor object
mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE Health_care")

mycursor.close()

# conecting to database
engine = create_engine('mysql+mysqlconnector://root:Root@123@localhost/health_care', echo =False)

mycursor.execute("Use Health_care")

# creating table structure in mysql
mycursor.execute(f'''CREATE TABLE IF NOT EXISTS health_care_table
(Patient_ID int,
Admit_Date Date, 
Discharge_Date Date, 
Diagnosis varchar(100),
Bed_Occupancy varchar(50),
Test varchar (50),
Doctor varchar (100),
Followup_Date Date,
Feedback float,
Billing_Amount int,
Health_Insurance_Amount float)
''')

# URL-encode the password
password = quote('Root@123')

# Connection string
connection_string = f'mysql+mysqlconnector://root:{password}@localhost/health_care'

# Create engine
engine = create_engine(connection_string, echo=True)

# Test connection
try:
    with engine.connect() as connection:
        print("SQLAlchemy connection successful!")
except Exception as e:
    print(f"SQLAlchemy connection failed: {e}")

# Inserting the data into the sql database
Healthcare_data.to_sql('health_care_table', engine, if_exists = 'replace', index = False,
                    dtype={'Patient_ID': sqlalchemy.types.Integer,
                            'Admit_Date':sqlalchemy.types.Date,
                            'Discharge_Date':sqlalchemy.types.Date,
                            'Diagnosis': sqlalchemy.types.VARCHAR(length=50),
                            'Bed_Occupancy':sqlalchemy.types.VARCHAR(length=50),
                            'Test':sqlalchemy.types.VARCHAR(length=50),
                            'Doctor':sqlalchemy.types.VARCHAR(length=50),
                            'Followup_Date':sqlalchemy.types.Date,
                            'Feedback':sqlalchemy.types.Float,
                            'Billing_Amount':sqlalchemy.types.Integer,
                            'Health_Insurance_Amount':sqlalchemy.types.Float})

                   
