from flask import Flask, request, jsonify, render_template
import pandas as pd
from textblob import TextBlob
import io
import re
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit


def clean_tweet(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def get_sentiment(text):
    cleaned = clean_tweet(text)
    if not cleaned:
        return "neutral", 0.0
    analysis = TextBlob(cleaned)
    polarity = round(analysis.sentiment.polarity, 4)
    if polarity > 0.05:
        return "positive", polarity
    elif polarity < -0.05:
        return "negative", polarity
    else:
        return "neutral", polarity


def detect_tweet_column(df):
    """Try to auto-detect the tweet text column."""
    candidates = ['text', 'tweet', 'content', 'message', 'body', 'full_text', 'tweet_text']
    for col in candidates:
        if col.lower() in [c.lower() for c in df.columns]:
            # return the actual column name with original casing
            for c in df.columns:
                if c.lower() == col.lower():
                    return c
    # fallback: return first string-heavy column
    for col in df.columns:
        if df[col].dtype == object:
            sample = df[col].dropna().head(5)
            avg_len = sample.astype(str).str.len().mean()
            if avg_len > 20:
                return col
    return df.columns[0]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filename = file.filename.lower()
    try:
        content = file.read()
        if filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(content), encoding='latin-1')
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            return jsonify({'error': 'Unsupported file type. Please upload CSV or Excel.'}), 400
    except Exception as e:
        return jsonify({'error': f'Could not parse file: {str(e)}'}), 400

    if df.empty:
        return jsonify({'error': 'File is empty'}), 400

    tweet_col = detect_tweet_column(df)
    tweets_raw = df[tweet_col].fillna('').astype(str).tolist()

    results = []
    for i, raw in enumerate(tweets_raw[:2000]):  # cap at 2000 for performance
        sentiment, score = get_sentiment(raw)
        results.append({
            'id': i,
            'original': raw[:300],
            'cleaned': clean_tweet(raw)[:300],
            'sentiment': sentiment,
            'score': score
        })

    positive = [r for r in results if r['sentiment'] == 'positive']
    negative = [r for r in results if r['sentiment'] == 'negative']
    neutral  = [r for r in results if r['sentiment'] == 'neutral']

    return jsonify({
        'total': len(results),
        'positive_count': len(positive),
        'negative_count': len(negative),
        'neutral_count': len(neutral),
        'columns': list(df.columns),
        'detected_column': tweet_col,
        'tweets': results
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)