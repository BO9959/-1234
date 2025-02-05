# stock_ai_analysis/news_analysis.py
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def get_stock_news(stock_symbol):
    url = f"https://news.google.com/search?q={stock_symbol}+stock"
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [h3.get_text() for h3 in soup.find_all("h3")[:5]]
        return headlines
    except Exception as e:
        return []

def analyze_news_sentiment(headlines):
    if not headlines:
        return 0
    sentiments = []
    for headline in headlines:
        try:
            polarity = TextBlob(headline).sentiment.polarity
            if abs(polarity) > 0.9:
                continue
            sentiments.append(polarity)
        except Exception:
            continue
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    return avg_sentiment
