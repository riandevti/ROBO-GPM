import time

from apscheduler.schedulers.background import BackgroundScheduler

from automation import run_all
from config import load_config

scheduler = BackgroundScheduler()


def start_scheduler():

    config = load_config()

    scheduler.remove_all_jobs()

    for t in config["general"]["run_times"]:

        hour, minute = map(int, t.split(":"))

        scheduler.add_job(
            run_all,
            "cron",
            hour=hour,
            minute=minute
        )

    if not scheduler.running:

        scheduler.start()


def stop_scheduler():

    if scheduler.running:

        scheduler.shutdown(wait=False)


def reload_scheduler():

    stop_scheduler()

    start_scheduler()


def scheduler_running():

    return scheduler.running