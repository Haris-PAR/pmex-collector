"""
PMEX Crop Collector — 15-Minute Scheduler
==========================================
Long-running process that calls crop_collector.collect() every 15 minutes.

Usage:
    python run_collector.py                  # run scheduler (every 15 min)
    python run_collector.py --interval 5     # custom interval in minutes
    python run_collector.py --once           # run once immediately, then exit

Run with nohup/tmux/screen for production:
    nohup .venv/bin/python run_collector.py >> scheduler.log 2>&1 &

Or use crontab:
    */15 * * * * cd /home/haris/Desktop/PAR/PMEX_V2 && .venv/bin/python crop_collector.py >> cron.log 2>&1
"""

import signal
import sys
import time
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import schedule

from crop_collector import collect

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

PST = ZoneInfo("Asia/Karachi")
DEFAULT_INTERVAL = 15  # minutes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scheduler.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("scheduler")

# ─────────────────────────────────────────────────────────────────────────────
# Graceful shutdown
# ─────────────────────────────────────────────────────────────────────────────

_shutdown = False


def _handle_signal(signum, frame):
    global _shutdown
    sig_name = signal.Signals(signum).name
    log.info(f"🛑 Received {sig_name} — shutting down after current cycle...")
    _shutdown = True


signal.signal(signal.SIGINT, _handle_signal)
signal.signal(signal.SIGTERM, _handle_signal)


# ─────────────────────────────────────────────────────────────────────────────
# Job wrapper
# ─────────────────────────────────────────────────────────────────────────────

_run_count = 0


def run_job():
    """Execute a single collection cycle with error handling."""
    global _run_count
    _run_count += 1
    now = datetime.now(tz=PST)

    log.info(f"{'═' * 60}")
    log.info(f"🔄 Run #{_run_count} — {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    log.info(f"{'═' * 60}")

    try:
        result = collect(force=False)
        status = result["status"]

        if status == "success":
            log.info(
                f"✅ Run #{_run_count} complete: "
                f"{result['active_stored']} stored, "
                f"{result['skipped_inactive']} skipped."
            )
        elif status.startswith("skipped"):
            log.info(f"⏭  Run #{_run_count}: {status}")
        else:
            log.error(
                f"❌ Run #{_run_count} failed: {result.get('error_message', 'unknown')}"
            )

    except Exception as exc:
        log.exception(f"💥 Run #{_run_count} — unhandled exception: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    # Parse --interval N
    interval = DEFAULT_INTERVAL
    if "--interval" in args:
        idx = args.index("--interval")
        if idx + 1 < len(args):
            try:
                interval = int(args[idx + 1])
            except ValueError:
                log.error(f"Invalid interval: {args[idx + 1]}")
                sys.exit(1)

    # --once mode
    if "--once" in args:
        log.info("🔄 Single run mode (--once)")
        run_job()
        return

    # --help
    if "--help" in args or "-h" in args:
        print(__doc__)
        return

    # ── Start scheduler ─────────────────────────────────────────────────
    log.info(f"🚀 PMEX Crop Collector Scheduler")
    log.info(f"   Interval:  every {interval} minutes")
    log.info(f"   Database:  pmex_crops.db")
    log.info(f"   PID:       {__import__('os').getpid()}")
    log.info(f"   Stop with: Ctrl+C or kill {__import__('os').getpid()}")
    log.info(f"{'─' * 60}")

    # Run immediately on start
    run_job()

    # Schedule recurring runs on fixed clock minutes
    if 60 % interval == 0:
        for m in range(0, 60, interval):
            schedule.every().hour.at(f":{m:02d}").do(run_job)
    else:
        schedule.every(interval).minutes.do(run_job)

    # Event loop
    while not _shutdown:
        schedule.run_pending()
        # Sleep in short intervals so we respond to signals quickly
        for _ in range(30):  # 30 × 1s = check every 30s
            if _shutdown:
                break
            time.sleep(1)

    log.info(f"👋 Scheduler stopped after {_run_count} runs. Goodbye!")


if __name__ == "__main__":
    main()
