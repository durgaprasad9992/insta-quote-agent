from agents import run_bot
import schedule
import time
import traceback

print("🚀 Instagram AI Bot Started...")

# Run immediately when container starts
try:
    run_bot()
except Exception as e:
    print("Error in first run:", e)
    traceback.print_exc()

# Run every 6 hours
schedule.every(6).hours.do(run_bot)

# Keep container alive forever
while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except Exception as e:
        print("Scheduler error:", e)
        traceback.print_exc()
        time.sleep(60)
