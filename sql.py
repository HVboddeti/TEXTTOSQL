import sqlite3

connection=sqlite3.connect("Student.db")



cursor=connection.cursor()

table_info="""
Create table STUDENT(Name varchar(25), Class Varchar(25), Section Varchar(25),Marks INT);
"""

cursor.execute(table_info)


cursor.execute('''INSERT INTO STUDENT VALUES ('Aarav Patel', '10th Grade', 'A', 88)''')

cursor.execute('''INSERT INTO STUDENT VALUES ('Sophia Williams', '10th Grade', 'B', 92)''')

cursor.execute('''INSERT INTO STUDENT VALUES ('Liam Johnson', '9th Grade', 'A', 76)''')

cursor.execute('''INSERT INTO STUDENT VALUES ('Emma Brown', '9th Grade', 'C', 84)''')

cursor.execute('''INSERT INTO STUDENT VALUES ('Noah Davis', '10th Grade', 'A', 95)''')

print("The Inserted Records are:")

data=cursor.execute('''Select * from Student''')

for row in data:
    print(row)


connection.commit()
connection.close()

