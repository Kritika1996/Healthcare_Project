import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px 
import seaborn as sns
import mysql.connector
import pandas as pd

# Global variable to hold connection
mydb = None
def get_connection():
    global mydb
    if mydb is None or not mydb.is_connected():
# Database connection (at the top level - only create ONCE)
        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Root@123",
                database="Health_care",
                autocommit=True
            )
        except Exception as e:
            st.error(f"Database connection error: {e}")
            st.stop()
    return mydb

# Function to execute queries 
def execute_query(query, fetchone=False):
    mydb = get_connection() # Get the connection 
    mycursor = mydb.cursor()
    try:
        #st.write(f"Executing query: {query}")
        mycursor.execute(query)
        if mycursor.description:
            if fetchone:
                data = mycursor.fetchone()
            else:
                data = mycursor.fetchall()
            return data
        else:
            return None
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        mycursor.close()
    
# Load the data
df = pd.read_excel(r"C:\Users\varun\OneDrive\Documents\Healthcare project VS\Healtcare-Dataset.xlsx")

st.title('Health Care Project')

page = st.sidebar.radio("Navigation", ["Home", "Business Cases"])
if page == "Home":
    st.header("Home Page")
    st.subheader("Project Overview")
    st.write("""Health care data is critical for improving patient care 
              and operational efficiency. However, analyzing large 
              volumes of patient and treatment data remains challenging.
               This project aims to build an interactive analytics 
              dashboard using Python, SQL, and Streamlit, providing 
              insights into patient demographics, treatment patterns,
               and facility utilization.""")
    
elif page == "Business Cases":
    st.header("Business Cases")
    st.sidebar.title("Filters")

    # Converting Admit_Date to datetime
    df['Admit_Date'] = pd.to_datetime(df['Admit_Date'])

    # Creating filters
    diagnosis_filter = st.sidebar.multiselect("Select Diagnoses", df['Diagnosis'].unique())
    doctor_filter = st.sidebar.multiselect("Select Doctors", df['Doctor'].unique())
    admission_month_filter = st.sidebar.multiselect("Select Admission Month", df['Admit_Date'].dt.month_name().unique())

    # Initializing the base query
    base_query = "SELECT * FROM health_care_table WHERE 1=1"

    # Applying filters to the base query
    if diagnosis_filter:
        diagnosis_filter_str = ', '.join(f"'{d}'" for d in diagnosis_filter)
        base_query += f" AND Diagnosis IN ({diagnosis_filter_str})"

    if doctor_filter:
        doctor_filter_str = ', '.join(f"'{d}'" for d in doctor_filter)
        base_query += f" AND Doctor IN ({doctor_filter_str})"

    if admission_month_filter:
        admission_month_filter_str = ', '.join(f"'{m}'" for m in admission_month_filter)
        base_query += f" AND MONTHNAME(Admit_Date) IN ({admission_month_filter_str})"

# Visuals creation (1)
if page == "Business Cases":
    st.markdown('<h1 style = "color: black;"> Trends in Admission Over Time</h1>', unsafe_allow_html = True)

  
    query_1 = f"""
            SELECT MONTHNAME(Admit_Date) AS Admission_Month, COUNT(Patient_ID) AS Total_Admissions
            FROM health_care_table
            WHERE 1=1
            {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
            {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
            {f'AND MONTHNAME(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
            GROUP BY Admission_Month
            ORDER BY Admission_Month;
        """
    data = execute_query(query_1)
    if data:
        df1 = pd.DataFrame(data, columns=['Admission_Month', 'Total_Admissions'])
    
        # Pivot the DataFrame (Necessary for Heatmap)
        df_pivot = df1.pivot_table(index="Admission_Month", values="Total_Admissions", aggfunc="sum")

        # Create Heatmap
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.heatmap(df_pivot, cmap="Greens", annot=True, fmt="d", linewidths=0.5, ax=ax)

        # Adding the title
        fig.suptitle("Trends in Admission Over Time", fontsize=14,fontweight = "semibold",ha="right")
        # Display in Streamlit
        st.pyplot(fig)

    # Visual creation (2)
    if page == "Business Cases":
        st.markdown('<h1 style = "color: black;"> Diagnosis Frequency Analysis </h1>', unsafe_allow_html = True)

        query_2 =  f"""SELECT Diagnosis, COUNT(Patient_ID) AS 
                    Total_Patient
                    FROM (
                    SELECT Diagnosis, Patient_ID
                    FROM health_care_table WHERE 1=1
                    {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                    {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                    {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                    ) AS filtered_data
                    GROUP BY Diagnosis  -- Correct: Group by Diagnosis
                    ORDER BY Total_Patient DESC
                    LIMIT 5;"""
        data = execute_query(query_2)
        if data:
            df2 = pd.DataFrame(data, columns=['Diagnosis', 'Total_Patient'])

            # Bar chart creation
            fig2 = px.bar(
                df2,
                x = "Diagnosis",
                y = "Total_Patient",
                title = "Diagnosis Frequency Analysis",
                labels = {"Diagnosis": "DIagnosis", "Total_Patient": "Total_Patient"},
                color_discrete_sequence=["green"]
            )
            st.plotly_chart(fig2)

    # Visual creation (3)
    if page == "Business Cases":
        st.markdown('<h1 style= "color: black;">Bed Occupancy Analysis <h1>', unsafe_allow_html=True )

        query_3 = f"""
            SELECT Bed_Occupancy, COUNT(*) AS Number_of_Patients
            FROM (
                SELECT Bed_Occupancy, Patient_ID 
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                GROUP BY Bed_Occupancy;  -- Correct: Group by Bed_Occupancy
                """
        data = execute_query(query_3)
        if data:
            df3 = pd.DataFrame(data, columns=['Bed_Occupancy',"Number_of_Patient"])

            # Pie Chart
            fig3 = px.pie(
                df3,
                names= "Bed_Occupancy",
                values="Number_of_Patient",
                title="Bed Occupied by Patients",
                color="Bed_Occupancy",
                hole=0,
                labels={"Bed_Occupancy":"Bed_Occupancy"}
            )
            st.plotly_chart(fig3)

# Visual creation (5)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Seasonal Admission Patterns <h1>', unsafe_allow_html=True)

    query_5=f"""
            SELECT monthname(Admit_Date) AS Admission_Month, COUNT(*) AS Total_Admission
            FROM (
                SELECT Admit_Date
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
            ) AS filtered_data
            GROUP BY Admission_Month 
            ORDER BY Admission_Month;
        """
    data = execute_query(query_5)
    if data:
        df5 = pd.DataFrame(data,columns=['Admission_Month','Total_Admission'])

        # converting Admission month to categorical data 

        fig5 = px.bar(
            df5,
            x = "Admission_Month",
            y = "Total_Admission",
            title = "Total Monthly Admission",
            labels = {"Admission_Month": "Admission_Month","Total_Admission": "Total_Admission"},
            color_discrete_sequence=["lightseagreen"]
        )
        st.plotly_chart(fig5)

# Visual creation (6)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Doctors Performance Analysis<h1>', unsafe_allow_html=True)

    query_6=f"""
            SELECT Doctor ,COUNT(Patient_ID) AS Total_Patient 
            FROM (
                SELECT Doctor, Patient_ID
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                GROUP BY Doctor
                ORDER BY Total_Patient DESC;
                """
    data = execute_query(query_6)
    if data:
        df6 = pd.DataFrame(data,columns=['Doctor','Total_Patient'])

        # Horizontal Bar chart 
        fig6 = px.bar(
            df6,
            x = "Total_Patient",
            y = "Doctor",
            title = "Patient Count by Doctor",
            labels = {"Total_Patient":"Total_Patient"},
            orientation = "h",
            color_discrete_sequence= ["lightgreen"]
        )
        st.plotly_chart(fig6)

# Visual creation (7)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Test Frequency Analysis <h1>', unsafe_allow_html=True)

    query_7=f"""
            SELECT Test, COUNT(Test) AS Test_Frequency 
            FROM (
                 SELECT Test
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                GROUP BY Test
                ORDER BY Test_Frequency DESC;
                """
    data = execute_query(query_7)
    if data:
        df7 = pd.DataFrame(data,columns=['Test','Test_Frequency'])

        # Vertical Bar chart
        fig7 = px.bar(
            df7,
            x = "Test",
            y = "Test_Frequency",
            title = "Test Count On Patient",
            color_discrete_sequence= ["lightseagreen"]
        )
        st.plotly_chart(fig7)

# Visual creation (8)
if page == "Business Cases":
    st.markdown('<h1 style="color:black"> Feedback Analysis <h1>', unsafe_allow_html=True)

    query_8=f"""
            SELECT Feedback, ROUND(AVG(`Billing Amount`),2) AS Avg_Billing 
            FROM (
                SELECT Feedback, `Billing Amount`
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                GROUP BY Feedback
                ORDER BY Feedback;
                """
    data = execute_query(query_8)
    if data:
        df8 = pd.DataFrame(data,columns=['Feedback','Avg_Billing'])

        # Bar Chart
        fig8 = px.bar(
            df8,
            x = "Avg_Billing",
            y = "Feedback",
            title = "Average Billing Of Patients",
            color_discrete_sequence=["red"],
            orientation='h'
        )
        st.plotly_chart(fig8)

# Visual creation (9)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Diagnosis-Specific Test Analysis <h1>', unsafe_allow_html=True)

    query_9=f"""
            SELECT Diagnosis, Test, COUNT(*) AS Test_count 
            FROM (
                SELECT Diagnosis, Test
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                group by Diagnosis, Test
                order by Diagnosis, Test_count desc;"""
    data = execute_query(query_9)
    if data:
        df9 = pd.DataFrame(data,columns=['Diagnosis','Test','Test_count'])

        # Grouped Bar chart
        fig9 = px.bar(
            df9,
            x = "Diagnosis",
            y = "Test_count",
            color = "Test",
            barmode="group",
            title = "Test Count by Diagnosis and Test",
            labels={"Tes_count":"Test_count"}
        )
        st.plotly_chart(fig9)

# Visual creation (10)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Bed Occupancy by Diagnosis<h1>', unsafe_allow_html=True)

    query_10=f'''select Bed_Occupancy, Diagnosis, count(*) as Patient_count
                from (SELECT Bed_Occupancy, Diagnosis
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                group by Bed_Occupancy, Diagnosis
                order by Bed_Occupancy, Patient_count desc;'''''
    data = execute_query(query_10)
    if data:
        df10 = pd.DataFrame(data,columns=['Bed_Occupancy','Diagnosis','Patient_count'])

        # Stacked Bar Chart
        fig10 = px.bar(
            df10,
            x = "Bed_Occupancy",
            y = "Patient_count",
            color = "Diagnosis",
            title = "Patient Count by Bed Occupancy and Diagnosis",
            labels={"Patient_count":"Patient_count"}
        )
        st.plotly_chart(fig10)

# Visual creation (11)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Doctor-Specific Diagnosis Analysis <h1>', unsafe_allow_html=True)

    query_11=f'''select Doctor, Diagnosis, count(*) as Patient_count
                from (select Doctor, Diagnosis
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data 
                group by Doctor, Diagnosis
                order by Doctor, Patient_count desc;'''
    data = execute_query(query_11)
    if data:
        df11 = pd.DataFrame(data,columns=['Doctor','Diagnosis','Patient_count'])

        # Grouped chart
        fig11 = px.bar(
            df11,
            x = "Doctor",
            y = "Patient_count",
            color= "Diagnosis",
            barmode= "group",
            title = "Doctor's Speciality",
            labels = {"Patient_count":"Patient_count"}
        )
        st.plotly_chart(fig11)

# Visual creation (12)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Follow-up Time Analysis <h1>', unsafe_allow_html=True)

    query_12=f'''select datediff( `Followup Date`, Admit_Date)  as Followup_Days,
                count(*) as Patient_count 
                from (select `Followup Date`, Admit_Date
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                group by Followup_Days;'''
    data = execute_query(query_12)
    if data:
        df12 = pd.DataFrame(data,columns=['Followup_Days','Patient_count'])

        ## Histogram chart
        fig12 = px.histogram(
            df12,
            x = "Followup_Days",
            y = "Patient_count",
            title = "Distribution of Follow-up Days",
            color_discrete_sequence=["Green"],
            labels = {"Followup_Days":"Followup_Days","Patient_count": "Patient_count"}

        )
        st.plotly_chart(fig12)

# Visual creation (13)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Health Insurance Utilization <h1>', unsafe_allow_html=True)

    query_13=f'''select `Health Insurance Amount` , count(Patient_ID) as Patient_count
                from (select `Health Insurance Amount`, patient_ID
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                group by `Health Insurance Amount`
                order by Patient_count desc;'''
    data = execute_query(query_13)
    if data:
        df13 = pd.DataFrame(data,columns=['Patient_count','Health Insurance Amount'])

        ## Bar chart
        fig13 = px.bar(
            df13,
            x="Patient_count",
            y="Health Insurance Amount",
            title = "Patient Count by Health Insurance Amount",
            labels={"Patient_count":"Patient_count","Health Insurance Amount":"Health Insurance Amount"},
            color_discrete_sequence=["lightgreen"],
            orientation='h'
            
        )
        st.plotly_chart(fig13)

# Visual creation (14)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Billing Amount by Diagnosis <h1>', unsafe_allow_html=True)

    query_14=f'''select Diagnosis,avg(`Billing Amount`)as Avg_Billing
                from (select Diagnosis, `Billing Amount`
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data  
                group by Diagnosis
                order by Avg_Billing desc;'''
    data = execute_query(query_14)
    if data:
        df14 = pd.DataFrame(data,columns=['Diagnosis','Avg_Billing'])

        ## Bar Chart

        fig14 = px.bar(
            df14,
            x = "Avg_Billing",
            y = "Diagnosis",
            title= "Average Billing as per Diagnosis",
            labels= {"Avg_Billing":"Avg_Billing","Diagnosis":"Diagnosis"},
            color_discrete_sequence=["limegreen"],
            orientation='h'
        )
        st.plotly_chart(fig14)

# Visual creation (15)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Seasonality Diagnosis <h1>', unsafe_allow_html=True)

    query_15=f'''select monthname(Admit_Date) as Admission_month,
                Diagnosis, count(*) as Patient_count 
                from (select Admit_Date, Diagnosis
                FROM health_care_table WHERE 1=1
                {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
                {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
                {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
                ) AS filtered_data
                group by Admission_month, Diagnosis
                order by Admission_month, Patient_count desc;'''
    data = execute_query(query_15)
    if data:
        df15 = pd.DataFrame(data,columns=['Admission_month','Diagnosis','Patient_count'])

        # Stacked Bar chart
        fig15 = px.bar(
            df15,
            x="Admission_month",
            y="Patient_count",
            color="Diagnosis",
            title = "Patient Admissions by Month and Diagnosis",
            labels={"Patient_count","Patient_count"}
        )
        st.plotly_chart(fig15)

#Visual creation (4)
if page == "Business Cases":
    st.markdown('<h1 style="color:black">Length of Stay Distribution</h1>', unsafe_allow_html=True)
    
    filters_applied_to_query_4 = st.checkbox("Apply filters to Length of Stay calculation")
    if filters_applied_to_query_4:
        query_4 = f"""SELECT 
        count(*) as Total_Patient,
        round(AVG(DATEDIFF(Discharge_Date, Admit_Date)),1) AS Avg_Length_of_Stay, 
        MAX(DATEDIFF(Discharge_Date, Admit_Date)) AS Max_Length_of_Stay 
        FROM 
        {f'AND Diagnosis IN ({",".join([f"\'{diag}\'" for diag in diagnosis_filter])})' if diagnosis_filter else ''}
        {f'AND Doctor IN ({",".join([f"\'{doc}\'" for doc in doctor_filter])})' if doctor_filter else ''}
        {f'AND monthname(Admit_Date) IN ({",".join([f"\'{month}\'" for month in admission_month_filter])})' if admission_month_filter else ''}
        ) AS filtered_data;""" 
    else:
        query_4 = """SELECT 
            COUNT(*) AS Total_Patient,
            ROUND(AVG(DATEDIFF(Discharge_Date, Admit_Date)),1) AS Avg_Length_of_Stay, 
            MAX(DATEDIFF(Discharge_Date, Admit_Date)) AS Max_Length_of_Stay 
         FROM 
            health_care_table;"""     

    result= execute_query(query_4,fetchone=True)
    
    if result:
            if result is not None and result != ():  # Check for None and empty tuple
                try:
                    df_4 = pd.DataFrame([{
                        "Total_Patient": int(result[0]) if result and result[0] is not None else 0,
                        "Avg_Length_of_Stay": float(result[1]) if result and result[1] is not None else 0.0,
                        "Max_Length_of_Stay": int(result[2]) if result and result[2] is not None else 0
                    }])
                    st.dataframe(df_4)
                except (TypeError, IndexError) as e:
                    st.error(f"Error processing data: {e}. Data: {result}")
                    st.write(f"Query executed: {query_4}")
            elif result is None:
                st.warning("No data returned from the query.")  # Handle None result
            else:  # result == ()
                st.warning("No matching rows found for the query.")

                # Display the DataFrame as a table in Streamlit
                st.dataframe(df_4)