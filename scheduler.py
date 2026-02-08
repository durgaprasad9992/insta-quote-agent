import schedule, time
from app import run_pipeline

schedule.every(6).hours.do(run_pipeline)

print("Agent running...")

while True:
    schedule.run_pending()
    time.sleep(30)
