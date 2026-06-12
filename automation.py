import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

from dotenv import load_dotenv
load_dotenv()

import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

driver = webdriver.Edge()

## script functions

def wait():
    time.sleep(config["wait_time"])

def write(id, text):
    element = WebDriverWait(driver, config["wait_time"]).until(
        EC.presence_of_element_located((By.ID, id))
    )
    element.clear()
    element.send_keys(text)
    
def clickxpath(xpath):
    element = WebDriverWait(driver, config["wait_time"]).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    element.click()
        




## automation steps functions


def login():
    username = os.getenv("ADMIN_USERNAME")
    password = os.getenv("ADMIN_PASSWORD")
    
    submitxpath = config["submitXPATH"]

    driver.get(config["login_url"])

    write("idLogin", username)
    wait()

    write("idSenha", password)
    wait()

    clickxpath(submitxpath)


def  searchreport():
    
    driver.get(config["search_url"])






## main script

login()

searchreport()

wait()

input("Press Enter to exit...")