# data_collector.py
import os
import pandas as pd
import yfinance as yf
import time
import logging
import json

# 設定 logging 格式
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 📂 設定快取目錄
CACHE_DIR = "cache"
AI_DATABASE = "ai_brain.json"  # AI 記憶庫
os.makedirs(CACHE_DIR, exist_ok=True)  # 確保快取資料夾存在

def load_ai_memory():
    """ 加載 AI 的記憶庫 """
    if os.path.exists(AI_DATABASE):
        with open(AI_DATABASE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_ai_memory(memory):
    """ 儲存 AI 的記憶庫 """
    with open(AI_DATABASE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)

def analyze_prediction_error(stock_symbol, actual_price, predicted_price, error_threshold=5):
    """ 若預測誤差超過閾值，則分析誤差原因並更新 AI 記憶庫 """
    error = abs(actual_price - predicted_price)
    if error > error_threshold:
        logging.info(f"🔍 {stock_symbol} 預測誤差 {error} 超過 {error_threshold}，進行 AI 分析")
        ai_memory = load_ai_memory()
        reason = f"AI 分析發現 {stock_symbol} 預測誤差超過 {error_threshold}，需要改進。"  # 模擬 AI 思考過程
        ai_memory[stock_symbol] = {
            "last_actual_price": actual_price,
            "last_predicted_price": predicted_price,
            "error": error,
            "reason": reason
        }
        save_ai_memory(ai_memory)
        logging.info(f"📚 AI 記憶庫已更新 {stock_symbol}")

def get_stock_data(stock_symbol, period="10y", interval="1d", max_retries=3, force_download=False):
    """
    下載股票數據，並儲存到本地快取，避免重複下載。確保 'Close' 欄位格式正確，解決時區錯誤。
    """
    try:
        cache_file = os.path.join(CACHE_DIR, f"{stock_symbol}_{interval}.csv")

        # **📂 嘗試讀取本地快取**
        if os.path.exists(cache_file) and not force_download:
            logging.info(f"📂 發現 {stock_symbol} 的本地快取，嘗試讀取...")
            df_last = pd.read_csv(cache_file, index_col="Date", parse_dates=True).tail(1)

            # **確保 index 是 tz-naive**
            last_cached_date = df_last.index[-1] if not df_last.empty else None
            if last_cached_date is not None and last_cached_date.tz is not None:
                last_cached_date = last_cached_date.tz_localize(None)

            # **取得最新的交易日**
            try:
                market_today = yf.download(stock_symbol, period="1d", interval="1d").index[-1].tz_localize(None)
            except Exception as e:
                logging.warning(f"⚠️ 無法獲取 {stock_symbol} 最新交易日，使用 `pd.Timestamp.today()` 代替")
                market_today = pd.Timestamp.today().normalize().tz_localize(None)

            # **檢查快取是否最新**
            if last_cached_date and last_cached_date >= market_today:
                logging.info(f"✅ {stock_symbol} 的數據已是最新！")
                df = pd.read_csv(cache_file, index_col="Date", parse_dates=True)  # 讀取完整數據
                return df

            logging.info(f"🔄 {stock_symbol} 的數據過舊，重新下載...")

        # **📥 下載新數據**
        for attempt in range(1, max_retries + 1):
            try:
                logging.info(f"📥 嘗試下載 {stock_symbol} 的數據 (第 {attempt} 次)...")
                stock = yf.Ticker(stock_symbol)
                df = stock.history(period=period, interval=interval)

                if df.empty:
                    raise ValueError(f"⚠️ {stock_symbol} 沒有可用數據！")

                # **處理 MultiIndex 欄位**
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.droplevel(0)  # 移除第一層索引

                # **確保 'Close' 欄位存在**
                if "Close" not in df.columns:
                    raise ValueError(f"❌ {stock_symbol} 缺少 'Close' 欄位，請檢查下載的數據")

                # **確保 'Close' 是數值型態並轉換為 Series**
                df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
                df.dropna(subset=["Close"], inplace=True)

                # **修正時區問題**
                if isinstance(df.index, pd.DatetimeIndex):
                    df.index = df.index.tz_localize(None)

                # **存入本地快取**
                df.to_csv(cache_file)
                logging.info(f"💾 {stock_symbol} 的數據已儲存到本地快取 ({cache_file})")

                return df

            except Exception as e:
                logging.warning(f"⚠️ {stock_symbol} 下載失敗: {str(e)}")
                if attempt < max_retries:
                    logging.info(f"🔄 等待 5 秒後重試...")
                    time.sleep(5)  # 等待 5 秒後重試
                else:
                    logging.error(f"❌ {stock_symbol} 數據下載完全失敗，請稍後再試！")
                    return None  # 放棄該股票的數據

    except Exception as e:
        logging.error(f"❌ 獲取 {stock_symbol} 數據時發生錯誤: {str(e)}")
        return None
