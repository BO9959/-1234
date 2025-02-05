# stock_ai_analysis/scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from main import run_report
from stock_ai_analysis.config import REPORT_INTERVAL

def start_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(run_report, 'interval', seconds=REPORT_INTERVAL)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    start_scheduler()
