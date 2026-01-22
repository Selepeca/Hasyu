import time
import configparser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

NAMES = [
    "FROM",
    "mail",
    "MESSAGE",
]

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-sync")
options.add_argument("--disable-default-apps")
options.add_argument("--disable-extensions")
options.add_argument("--disable-notifications")
options.add_argument("--disable-gcm")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--log-level=3")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

lifespan = 20
count = 0

try:
    while True:
        config = configparser.ConfigParser()
        config.read("hosyu.ini", encoding="utf-8")

        URL = config["settings"]["url"]
        INTERVAL_SECONDS = int(config["settings"]["interval_seconds"])
        VALUES = [
            config["settings"]["from"],
            config["settings"]["mail"],
            config["settings"]["message"],
        ]

        inputs = dict(zip(NAMES, VALUES))

        count += 1
        if count >= lifespan:
            print("-- Instance Recreate --")
            driver.quit()
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 20)
            count = 0

        driver.get(URL)

        try:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "rise-interstitial-close-button")
                )
            )
            close_button.click()
        except TimeoutException:
            pass

        for name, value in inputs.items():
            if name == "MESSAGE":
                field = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            f'//textarea[contains(@class,"formelem") and @name="{name}"]',
                        )
                    )
                )
            else:
                field = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            f'//input[contains(@class,"formelem") and @name="{name}"]',
                        )
                    )
                )

            field.clear()
            field.send_keys(value)

        write_button = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "submitbtn"))
        )
        write_button.click()

        try:
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f'//input[@name="submit" and @type="submit" and @value="上記全てを承諾して書き込む"]',
                    )
                )
            )
            submit_button.click()
        except TimeoutException:
            pass

        now = datetime.now()
        print(now.strftime("[%Y/%m/%d %H:%M] 書き込みました"))

        time.sleep(INTERVAL_SECONDS)

except KeyboardInterrupt:
    pass

finally:
    driver.quit()
