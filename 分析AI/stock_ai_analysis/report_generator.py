import os
import pandas as pd
import logging
from stock_ai_analysis.config import REPORT_OUTPUT, EMAIL_SETTINGS
from stock_ai_analysis.email_sender import send_email
from stock_ai_analysis.data_collector import get_stock_data
from stock_ai_analysis.technical_analysis import add_technical_indicators
from stock_ai_analysis.ai_model import train_model_for_stock, predict_next_price
from stock_ai_analysis.news_analysis import get_stock_news, analyze_news_sentiment

def generate_report(data, output_path="reports/stock_report.csv"):
    """
    生成或追加分析报告至 CSV 文件
    """
    try:
        # 确保目标目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 检查数据是否有效
        if not data or not isinstance(data, list):
            raise ValueError("❌ 报告数据无效或为空")

        logging.info(f"📄 开始生成/更新报告: {output_path}")

        df_new = pd.DataFrame(data)
        if os.path.exists(output_path):
            df_existing = pd.read_csv(output_path)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_csv(output_path, index=False)
        logging.info(f"✅ 报告已更新: {output_path}")
        return output_path
    
    except Exception as e:
        logging.error(f"❌ 生成报告失败: {str(e)}")
        return None

def email_report(report_path):
    """
    呼叫 send_email 將報告檔案寄送給指定收件人
    """
    subject = "每小時股票分析報告 (含短期/長期預測、新聞情緒與誤差檢討)"
    body = "請參閱附件中的股票分析報告。"
    send_email(subject, body, EMAIL_SETTINGS.get("to_emails"),
               attachment_path=report_path,
               smtp_server=EMAIL_SETTINGS.get("smtp_server"),
               smtp_port=EMAIL_SETTINGS.get("smtp_port"),
               username=EMAIL_SETTINGS.get("username"),
               password=EMAIL_SETTINGS.get("password"))

def load_stock_list(file_path="stocks.csv"):
    """ 載入股票列表 """
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
            # 获取数据并进行分析
            data = get_stock_data(symbol)
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
            error_analysis = f"短期预测误差: {error:.2f}" if error > 5 else "无重大误差"

            # 添加数据到报告列表
            report_data.append({
                "symbol": symbol,
                "category": category,
                "latest_close": latest_close,
                "predicted_price_short": predicted_price_short,
                "predicted_price_long": predicted_price_long,
                "news_sentiment": news_sentiment,
                "news_headlines": news_headlines,
                "error_analysis": error_analysis,
                "Report_Time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            logging.info(f"{symbol} 分析完成")

        except Exception as inner_e:
            logging.error(f"Error processing {symbol}: {str(inner_e)}")
            continue

    # 调用 generate_report 生成或追加数据到报告文件
    report_path = generate_report(report_data, output_path="reports/stock_report.csv")
    logging.info("報告產生完成")
    email_report(report_path)