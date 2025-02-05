import numpy as np
import tensorflow as tf
from tensorflow import Sequential
from tensorflow import LSTM, Dense, Dropout
import logging
import json
import os

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

AI_MEMORY_FILE = "ai_brain.json"  # 存儲 AI 記憶

def load_ai_memory():
    """ 加載 AI 的記憶庫 """
    if os.path.exists(AI_MEMORY_FILE):
        with open(AI_MEMORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_ai_memory(memory):
    """ 儲存 AI 的記憶庫 """
    with open(AI_MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)

def analyze_prediction_error(stock_symbol, actual_price, predicted_price, error_threshold=5):
    """ 若預測誤差超過閾值，則分析誤差原因並更新 AI 記憶庫 """
    error = abs(actual_price - predicted_price)
    if error > error_threshold:
        logging.info(f"🔍 {stock_symbol} 預測誤差 {error} 超過 {error_threshold}，進行 AI 分析")
        ai_memory = load_ai_memory()
        reason = f"AI 分析發現 {stock_symbol} 預測誤差超過 {error_threshold}，需要改進。"  
        ai_memory[stock_symbol] = {
            "last_actual_price": actual_price,
            "last_predicted_price": predicted_price,
            "error": error,
            "reason": reason
        }
        save_ai_memory(ai_memory)
        logging.info(f"📚 AI 記憶庫已更新 {stock_symbol}")

def train_model_for_stock(stock_symbol, data, window=10):
    """
    使用 LSTM 训练模型来预测股价。
    """
    try:
        logging.info(f"📈 训练 {stock_symbol} 的 LSTM 模型...")
        
        data = data["Close"].values
        logging.debug(f"原始数据形状: {data.shape}")

        x_train, y_train = [], []

        for i in range(len(data) - window):
            x_train.append(data[i:i+window])
            y_train.append(data[i+window])

        x_train, y_train = np.array(x_train), np.array(y_train)
        logging.debug(f"x_train 形状: {x_train.shape}, y_train 形状: {y_train.shape}")

        x_train = x_train.reshape((x_train.shape[0], x_train.shape[1], 1))
        logging.debug(f"x_train 调整后的形状: {x_train.shape}")

        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(window, 1)),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit(x_train, y_train, epochs=10, batch_size=16, verbose=1)

        return model

    except Exception as e:
        logging.error(f"❌ 训练 {stock_symbol} 模型失败: {str(e)}")
        raise  # 抛出异常以便更好地调试

def predict_next_price(model, data, window=10):
    """
    使用 LSTM 預測未來股價
    """
    try:
        data_values = np.array(data["Close"].values)  # 確保是 NumPy array
        input_data = data_values[-window:].reshape(1, window, 1)  # 正確格式

        predicted_price = model.predict(input_data)

        return float(predicted_price[0][0])

    except Exception as e:
        logging.error(f"❌ 預測股價失敗: {str(e)}")
        print(f"📊 data_values type: {type(data_values)}, shape: {data_values.shape}")
        print(f"📊 input_data type: {type(input_data)}, shape: {input_data.shape}")
        return None
