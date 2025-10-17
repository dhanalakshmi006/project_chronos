# Project Chronos: The AI Archeologist

**Student Name:** Dhanalakshmi Nadar
**Student ID:** SE25UCSE076

---

## 📖 Project Description

**Project Chronos: The AI Archeologist** is a tool designed to reconstruct incomplete or obscure fragments, translating abbreviations, memes, and cultural slang into clear, modern English.


The application uses **Google Gemini** to interpret and fill in the missing context, and to provide certain keywords that are later used by **Google Custom Search** to find relevant historical and cultural sources about the fragment. It provides a **Reconstruction Report**, with the following:
1) The original text fragment  
2) The reconstructed fragment
3) Short explanations for old slang or references  used for the reconstruction.
4) Links to contextual sources for further information.

## ⚙️ Setup Instructions

Follow the steps below to set up and run Project Chronos on your local machine.

**Step 1:** Clone the Repository
Open a terminal or command prompt and run:

git clone https://github.com/dhanalakshmi006/project_chronos.git
cd project_chronos

**Step 2:** Create and Activate a Virtual Environment
python -m venv venv
# Activate the environment:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

 **Step 3:** Install Dependencies
pip install -r requirements.txt

**Step 4:**  Set up API Keys
1) Create a file names ".env" in the project folder.
 2) Ass the following lines in that folder:
 GEMINI_API_KEY=your_gemini_api_key_here (please Modify)
GOOGLE_CSE_KEY=your_google_custom_search_key_here (Modify)
GOOGLE_CX=your_custom_search_engine_id_here (Modify)

## **Usage Guide**
To open the web interface of the tool, you must type "python app.py" in your terminal inside the project folder.
Then you must open the given link in your browser to access the tool. The link will be in the format "http://127.0...."

Now the web interface will be open, It will ask you to enter the frangment to reconstruct the text!



