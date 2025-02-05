# stock_ai_analysis/config.py
# 全域設定

# 股票分類設定（請根據實際需求擴充）
STOCK_CATEGORIES = {
    "科技股": ["AAPL", "NVDA", "AMD", "TSLA"],
    "虛擬貨幣股": ["COIN", "MSTR"],
    "能源股": ["XOM", "BP"],
    "金融股": ["JPM", "GS"],
    "傳統產業": ["WMT", "KO"]
}

# 報告輸出檔案位置（CSV 格式）
REPORT_OUTPUT = "reports/stock_report.csv"

# 報告產生間隔（秒）：例如 3600 秒＝1 小時
REPORT_INTERVAL = 3600

# Email 設定（請填入實際 Email 資訊，注意安全性）
EMAIL_SETTINGS = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "guanzhili101@gmail.com",
    "password": "wyrb atoq xybp ofjp",
    "to_emails": ["guanzhili101@gmail.com"]
}
