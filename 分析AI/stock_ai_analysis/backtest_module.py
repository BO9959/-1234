import os
import pandas as pd
import yfinance as yf
import time
import logging

# 設定 logging 格式
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# 📂 設定快取目錄
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)  # 確保快取資料夾存在

def get_stock_data(stock_symbol, period="10y", interval="1d", max_retries=3, force_download=False):
    """
    下載股票數據，並儲存到本地快取，避免重複下載。優化快取比對方式，提高速度。
    """
    try:
        cache_file = os.path.join(CACHE_DIR, f"{stock_symbol}_{interval}.csv")

        # **📂 優化快取判斷**
        if os.path.exists(cache_file) and not force_download:
            file_modified_time = os.path.getmtime(cache_file)  # 取得檔案最後修改時間
            last_modified_date = pd.Timestamp(file_modified_time, unit="s").normalize()
            today = pd.Timestamp.today().normalize()

            if last_modified_date >= today:
                logging.info(f"✅ {stock_symbol} 的數據已是最新！（快取時間: {last_modified_date}）")
                return pd.read_csv(cache_file, index_col="Date", parse_dates=True)  # 只在需要時才讀取 CSV

            logging.info(f"🔄 {stock_symbol} 的數據過舊（最後更新: {last_modified_date}），重新下載...")

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
