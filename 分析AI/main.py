import pandas as pd
import logging
from stock_ai_analysis.config import EMAIL_SETTINGS
from stock_ai_analysis.data_collector import get_stock_data
from stock_ai_analysis.technical_analysis import add_technical_indicators
from stock_ai_analysis.ai_model import train_model_for_stock, predict_next_price
from stock_ai_analysis.news_analysis import get_stock_news, analyze_news_sentiment
from stock_ai_analysis.report_generator import generate_report, email_report
from stock_ai_analysis.email_sender import send_email
from stock_ai_analysis.error_analysis import record_error

logging.basicConfig(level=logging.INFO)


def load_stock_list(file_path="stocks.csv"):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        logging.error(f"Error loading stock list: {str(e)}")
        return pd.DataFrame(columns=["symbol", "category"])


def run_report():
    logging.info("開始產生報告")
    stock_list = load_stock_list()
    report_data = []

    for idx, row in stock_list.iterrows():
        symbol = row["symbol"]
        category = row["category"]
        try:
            # ✅ **加速數據讀取，避免多次下載**
            data = get_stock_data(symbol)
            if data is None or data.empty:
                raise ValueError(f"{symbol} 沒有數據")

            # ✅ **確保 'Close' 欄位正確**
            if "Close" not in data.columns:
                raise ValueError(f"{symbol} 缺少 'Close' 欄位")

            logging.info(f"📊 {symbol} 分析中...")
            data = add_technical_indicators(data)
            model_short = train_model_for_stock(symbol, data, window=10)
            predicted_price_short = predict_next_price(model_short, data, window=10)
            model_long = train_model_for_stock(symbol, data, window=50)
            predicted_price_long = predict_next_price(model_long, data, window=50)
            headlines = get_stock_news(symbol)
            news_sentiment = analyze_news_sentiment(headlines)
            news_headlines = "; ".join(headlines)
            latest_close = data["Close"].iloc[-1]
            error = abs(latest_close - predicted_price_short)
            error_analysis = "無重大誤差"

            if error > 5:
                reason = f"短期預測誤差過大，誤差={error:.2f}"
                record_error(category, symbol, "10天", latest_close, predicted_price_short, reason)
                error_analysis = reason

            report_data.append({
                "symbol": symbol,
                "category": category,
                "latest_close": latest_close,
                "predicted_price_short": predicted_price_short,
                "predicted_price_long": predicted_price_long,
                "news_sentiment": news_sentiment,
                "news_headlines": news_headlines,
                "error_analysis": error_analysis
            })
            logging.info(f"✅ {symbol} 分析完成")
        except Exception as inner_e:
            logging.error(f"❌ Error processing {symbol}: {str(inner_e)}")
            continue

    report_path = generate_report(report_data)
    logging.info("📄 報告產生完成")
    email_report(report_path)


if __name__ == "__main__":
    run_report()
