NUS HacknRoll 2026 thing



ModMatch is a semantic comparison tool designed to help National University of Singapore (NUS) students plan their Student Exchange Programme (SEP). It uses semantic similarity to match NUS modules with courses from partner universities, ensuring that module descriptions align even when titles differ.


Features
- Semantic Search: Uses Natural Language Processing (NLP) to compare module descriptions, identifying matches that keywords alone might miss.
- Persistence: Your progress is saved automatically. Every pairing added or removed is instantly mirrored to a local /data storage folder.
- Import: Easily expand your database. Import new module lists (e.g., from a specific partner university) and they will be appended to your existing records without overwriting them.
- Interactive Planning: Select modules from side-by-side tables, generate similarity scores, and review matches before adding them to your final plan.

Installation
1. Clone the repository:
```Bash
git clone https://github.com/yourusername/modmatch.git
cd modmatch
```

2. Install dependencies:
```Bash
pip install -r requirements.txt
```

3. Run the application:
```Bash
streamlit run app.py
```