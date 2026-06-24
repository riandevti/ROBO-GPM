import os
import sys
import json
import time
import shutil
import zipfile
import threading

from pathlib import Path
from datetime import datetime
from threading import Thread
from urllib.parse import urlencode

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager # type: ignore

from logger import logger, setup_logger
from apscheduler.schedulers.blocking import BlockingScheduler

# ================= BASE DIR =================

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent


load_dotenv(BASE_DIR / ".env")


with open(BASE_DIR / "config.json", "r", encoding="utf-8") as f:
    config = json.load(f)


setup_logger(BASE_DIR / config["general"]["log_folder"])


# ================= DRIVER =================

def create_driver(download_path):

    options = Options()

    prefs = {
        "download.default_directory": str(download_path),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }

    options.add_experimental_option("prefs", prefs)

    options.add_argument(f"--user-data-dir={download_path}/chrome_profile")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

# ================= SET FUNCTIONS =================

def wait_download(download_folder, destination_folder, final_name):
    start = time.time()

    while time.time() - start < 120:

        zip_files = list(Path(download_folder).glob("*.zip"))

        if zip_files:

            latest_zip = max(zip_files, key=lambda f: f.stat().st_mtime)

            if not any(f.suffix == ".crdownload" for f in zip_files):

                return process_zip(latest_zip, destination_folder, final_name)

        time.sleep(1)

def process_zip(zip_path, destination_folder, final_name):

    temp_folder = zip_path.parent / "temp_extract"

    if temp_folder.exists():
        shutil.rmtree(temp_folder)

    temp_folder.mkdir()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_folder)

    csv_files = list(temp_folder.glob("*.csv"))

    if not csv_files:
        raise Exception("No CSV inside zip")

    csv_file = csv_files[0]

    final_file = Path(destination_folder) / final_name

    if final_file.exists():
        final_file.unlink()

    shutil.move(str(csv_file), str(final_file))

    shutil.rmtree(temp_folder)

    zip_path.unlink()

    logger.info(f"Saved: {final_file}")
# ================= GPM =================

def run_gpm():


    cfg = config["gpm"]

    download_folder = Path(cfg["download_folder"])
    destination_folder = Path(cfg["destination_folder"])

    download_folder.mkdir(parents=True, exist_ok=True)
    destination_folder.mkdir(parents=True, exist_ok=True)

    driver = create_driver(download_folder)

    try:
        logger.info("GPM started")

        driver.get(cfg["login_url"])

        driver.find_element(By.ID, "idLogin").send_keys(os.getenv("ADMIN_USERNAME"))
        driver.find_element(By.ID, "idSenha").send_keys(os.getenv("ADMIN_PASSWORD"))

        driver.find_element(By.XPATH, cfg["submit_xpath"]).click()

        time.sleep(3)

        today = datetime.now().strftime("%d/%m/%Y")

        params = {
            "isMobile": "0",
            "data_inicial": cfg["initial_date"],
            "data_final": today,
            "contrato[]": cfg["contract_id"]
        }

        url = cfg["export_url"] + "?" + urlencode(params, doseq=True)

        driver.get(url)

        logger.info("GPM download triggered")

        wait_download(download_folder, destination_folder, "OBRAS.csv")

    except Exception as e:
        logger.exception(f"GPM error: {e}")

    finally:
        driver.quit()


# ================= TICKETLOG =================

def run_ticketlog():

    cfg = config["ticketlog"]

    download_folder = Path(cfg["download_folder"])
    destination_folder = Path(cfg["destination_folder"])

    download_folder.mkdir(parents=True, exist_ok=True)
    destination_folder.mkdir(parents=True, exist_ok=True)

    driver = create_driver(download_folder)

    try:
        logger.info("Ticketlog started")

        driver.get(cfg["login_url"])

        driver.find_element(By.ID, cfg["login_id"]).send_keys(os.getenv("ADMIN_USERNAME"))
        driver.find_element(By.ID, cfg["password_id"]).send_keys(os.getenv("ADMIN_PASSWORD"))

        driver.find_element(By.XPATH, cfg["submit_xpath"]).click()

        time.sleep(3)

        driver.find_element(By.XPATH, cfg["filter_xpath"]).click()
        driver.find_element(By.XPATH, cfg["download_button_xpath"]).click()

        logger.info("Ticketlog download triggered")

        time.sleep(20)  # aqui depois você melhora com wait inteligente

    except Exception as e:
        logger.exception(f"Ticketlog error: {e}")

    finally:
        driver.quit()


# ================= PARALLEL =================

def run_all():

    logger.info("START PARALLEL RUN")

    t1 = Thread(target=run_gpm)
    t2 = Thread(target=run_ticketlog)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    logger.info("ALL FINISHED")


# ================= SCHEDULER =================

if __name__ == "__main__":


    from apscheduler.schedulers.blocking import BlockingScheduler

    scheduler = BlockingScheduler()

    for t in config["general"]["run_times"]:
        scheduler.add_job(run_all, "cron", hour=int(t.split(":")[0]), minute=int(t.split(":")[1]))

    if config["general"]["run_on_startup"]:
        run_all()

    logger.info("Scheduler running")

    if config["general"].get("enable_scheduler", False):
        scheduler.start()
else:
    logger.info("Scheduler disabled (test mode)")
    run_all()