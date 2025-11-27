# mini-ai-interview-screener
Mini AI Interview Screener

The Mini AI Interview Screener is a lightweight application that conducts short, automated AI-powered interview screenings. It helps recruiters, students, and developers quickly evaluate candidates through structured questions and real-time AI responses.

🚀 Features

⚡ AI-Generated Interview Questions based on selected role/skills

🎤 Candidate Response Input (text-based)

🤖 AI-Powered Evaluation of answers

📊 Score & Feedback Summary

🌐 Lightweight FastAPI/Flask Backend (depending on your code)

🎯 Easy to Deploy on Render / Vercel / Localhost

📂 Project Structure
mini-ai-interview-screener/
│
├── app/
│   ├── main.py         # Main backend logic
│   ├── model/          # LLM/ML models or prompts (if any)
│   ├── utils/          # Utility functions
│   └── templates/      # Frontend HTML (if using)
│
├── requirements.txt     # Dependencies
├── .gitignore
└── README.md

📦 Installation

Clone the repo

git clone https://github.com/ChanduPulluru/mini-ai-interview-screener.git
cd mini-ai-interview-screener


Install dependencies

pip install -r requirements.txt


Run the application

python app/main.py

📝 How It Works

Choose your interview domain (Python, ML, Web Dev, etc.)

The AI generates 5–7 screening questions

User gives responses

AI evaluates:

correctness

clarity

depth

relevance

Final score + feedback is displayed

🛠️ Technologies Used

Python

FastAPI / Flask

OpenAI / Local LLM

HTML / JS (optional)

📈 Future Enhancements

🔊 Voice-based interview mode

👤 Candidate report download (PDF)

🧠 Adaptive question difficulty

🎥 Video interview support

💾 Database for storing results

🤝 Contributing

Contributions are welcome!
Feel free to fork the repo and submit a pull request.
