# TweetLens 🔍🐦

TweetLens is a web application that analyzes the sentiment of tweets using NLP.

## 🚀 Features
- Upload CSV or Excel files
- Automatic tweet column detection
- Sentiment analysis (Positive, Negative, Neutral)
- Interactive UI with filters and search
- Real-time tweet visualization

## 🛠️ Tech Stack
- Python (Flask)
- Pandas
- TextBlob (NLP)
- HTML/CSS/JS

## ⚙️ How It Works
1. Upload a dataset of tweets
2. Backend processes using Flask
3. TextBlob assigns sentiment polarity
4. Results displayed in UI

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/TweetLens.git
cd TweetLens

python -m venv venv
source venv/Scripts/activate   # Windows

pip install -r requirements.txt
python -m textblob.download_corpora

python app.py