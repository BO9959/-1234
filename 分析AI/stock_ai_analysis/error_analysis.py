# stock_ai_analysis/error_analysis.py
import os
import datetime

def record_error(category, symbol, timeframe, actual, predicted, reason):
    """
    當預測與實際數據差距超過 5 元時，記錄檢討結果到對應分類的錯誤檔
    timeframe: 如 "10天"、"50天" 或 "Day X"
    """
    filename = f"errors_{category}.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_message = (f"{timestamp} - {symbol} ({timeframe}) | Actual: {actual}, "
                     f"Predicted: {predicted} | Reason: {reason}\n")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(error_message)
