from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(question,prompt):
    model=genai.GenerativeModel('gemini-2.5-flash')
    response=model.generate_content([prompt[0],question])
    return response.text


def read_sql_query(sql,db):
    conn=sqlite3.connect(db)
    cursor=conn.cursor()
    cursor.execute(sql)
    rows=cursor.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows

prompt=[
    """
    You are an expert in converting English questions to SQL query!
    The SQL database has the name Student and has the following columns - Name, Class, Section \n\n
    For example, \nExample 1- How many entries of records are present?, the SQL command will be something
    like this SELECT COUNT(*) FROM Student;
    \nExample 2- Tell me all the students studying in Data Science class?, the SQL command will be
    something like this SELECT * FROM Student where CLASS="Data Science";
    also the sql code should not have ''' in beginning or end and sql word in the output
    """
]



st.set_page_config(page_title="I can retieve any SQL query")
st.header("Gemini App to Retrieve SQL Data")

question=st.text_input("Input: ",key="input")

submit=st.button("Ask the question")


if submit:
    response=get_gemini_response(question,prompt)
    print(response)
    data=read_sql_query(response,"Student.db")
    st.subheader("The Response is ")
    for row in data:
        print(row)
        st.header(row)