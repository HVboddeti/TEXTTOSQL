# 🧠 Text-to-SQL RAG Chatbot using Google Gemini
Author: Harsha Boddeti

This project demonstrates how to build a Text-to-SQL chatbot that translates natural language questions into SQL queries and retrieves results from a database — powered by Google Gemini (Generative AI) and Streamlit.

It uses a Retrieval-Augmented Generation (RAG) approach conceptually — where the model is guided with schema context (prompt engineering) to accurately query an existing SQLite sales/student database.

## 🚀 Features
- 🗣️ Converts natural English questions to valid SQL queries
- 🧮 Executes generated queries on a local SQLite database
- 📊 Displays the results in a user-friendly Streamlit interface
- 🔐 Uses .env for secure API key storage
- 🤖 Powered by Google Gemini API for natural language understanding

## 🧩 Project Structure
```
Text-to-SQL-RAG-Chatbot/
│
├── app.py                # Streamlit application logic
├── sql.py                # Creates and populates the Student.db database
├── Student.db            # SQLite database file
├── .env                  # Contains Gemini API key
├── requirements.txt      # Python dependencies
└── README.md             # Documentation
```

## ⚙️ Setup Instructions
1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Text-to-SQL-RAG-Chatbot.git
cd Text-to-SQL-RAG-Chatbot
```

2️⃣ Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate      # On Mac/Linux
venv\Scripts\activate         # On Windows
```

3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

4️⃣ Add Your Gemini API Key
Create a .env file (already included in your repo) and add your key:
```
Gemini_API_Key="YOUR_GEMINI_API_KEY"
```

5️⃣ Run Database Setup
```bash
python sql.py
```
This script creates the STUDENT table and inserts 5 sample records into Student.db.

6️⃣ Run the Streamlit App
```bash
streamlit run app.py
```
Then open the local URL shown in the terminal (usually http://localhost:8501/).

## 🧠 How It Works
- **User Input:** The user enters a question in plain English — for example, “Show me all students in Class 10th Grade”.
- **Prompt Engineering (RAG-like Context):** The system uses a predefined prompt containing table schema and examples to guide the LLM (Gemini).
- **LLM Query Generation:** Gemini converts the natural question into a valid SQL command, e.g. `SELECT * FROM STUDENT WHERE Class="10th Grade";`.
- **Database Execution:** The SQL command is executed on the local SQLite database (Student.db).
- **Result Display:** Results are fetched and displayed on the Streamlit app.

## 🧭 Architecture Diagram
Architecture Diagram

## 🧰 Tech Stack
| Component | Technology |
| --- | --- |
| Frontend | Streamlit |
| Backend | Python |
| Database | SQLite |
| AI Model | Google Gemini 2.5 Flash |
| Environment Management | python-dotenv |
| Dependencies | streamlit, google-generativeai, python-dotenv |

## 🧪 Example Queries
| Natural Language | Generated SQL | Output |
| --- | --- | --- |
| How many records are in the table? | `SELECT COUNT(*) FROM STUDENT;` | 5 |
| List all students from 10th Grade | `SELECT * FROM STUDENT WHERE Class="10th Grade";` | Aarav Patel, Sophia Williams, Noah Davis |
| Who scored the highest marks? | `SELECT Name, Marks FROM STUDENT ORDER BY Marks DESC LIMIT 1;` | Noah Davis – 95 |

## 🔐 Environment Variables
| Variable | Description |
| --- | --- |
| Gemini_API_Key | Your Google Generative AI API key |

## Results
Result.mp4

## 📘 Future Enhancements
- 🧩 Extend schema to Sales Transactions dataset (Customers, Orders, Products)
- 🧠 Implement true RAG pipeline with schema embedding & retriever
- 📈 Add charts and analytics with Streamlit visualization
- ☁️ Deploy on Streamlit Cloud or Google Cloud Run

## 👨‍💻 Author
Harsha Boddeti
AI Engineer | Data & Backend Developer
- 🔗 LinkedIn
- 📧 hv.boddeti@gmail.com
