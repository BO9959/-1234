# stock_ai_analysis/technical_analysis.py
import ta
import pandas as pd
import numpy as np

def add_technical_indicators(df):
    """
    根據股價數據新增技術指標欄位
    """
    try:
        # **檢查 'Close' 是否存在**
        if "Close" not in df.columns:
            print("Error: 無法計算技術指標，'Close' 欄位不存在")
            raise KeyError("'Close' column is missing in DataFrame")

        df["SMA_50"] = ta.trend.sma_indicator(df["Close"], window=50)
        df["SMA_200"] = ta.trend.sma_indicator(df["Close"], window=200)
        df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()

        return df
    except Exception as e:
        raise Exception(f"Error calculating technical indicators: {str(e)}")

