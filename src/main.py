# import sys
# Change to False if not debugging lmao
# Affects webdriver headless mode
DEBUG = True
# DEBUG = bool(hasattr(sys, 'gettrace') and sys.gettrace() is not None)

import os
import requests

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.firefox.webdriver import WebDriver
def initializeDriver() -> WebDriver:
    from selenium.common import exceptions
    if not DEBUG: os.environ['MOZ_HEADLESS']='1'
    try:
        driver = webdriver.Firefox()
    except exceptions.WebDriverException:
        print(f"The Firefox webdriver (geckodriver) is not installed or not in PATH. Make sure both of these requirements are satisfied, then try again.")
        exit(1)
    except:
        print("Uh oh, something happened while trying to initialize the webdriver!")
        exit(2)
    return driver

# TODO: change URL to sim.13lo.pl when done
URL = "http://127.0.0.1:8081"
driver = initializeDriver()

def submit(problemID:int, submissionSourceFilePath:str) -> None:
    if not os.path.exists(submissionSourceFilePath):
        print(f"ERROR: The file {submissionSourceFilePath} does not exist.")
        return
    driver.get(f"{URL}/c/p{problemID}/submit")
    try:
        # fileBox = driver.find_element(By.NAME, "solution")
        fileBox = WebDriverWait(driver, 15).until(lambda d: d.find_element(By.NAME, "solution"))
    except TimeoutException:
        print("Submission page timed out")
        return
    # Now the page is sure to have been loaded
    fileBox.send_keys(submissionSourceFilePath)
    sendBtn = driver.find_element(By.XPATH, "//input[@type='submit']")
    sendBtn.click()
    # TODO: add wait for response (possible error!)

def getStatementURL(problemID:int) -> str:
    return f"{URL}/api/download/statement/contest/p{problemID}/"

def openStatement(problemID:int) -> None:
    from subprocess import call
    call(["xdg-open", getStatementURL(problemID)])

def downloadStatement(problemID:int) -> None:
    with open(f"{problemID}.pdf", "wb") as f:
        f.write(requests.get(getStatementURL(problemID)).content)
    print(f"Saved statement to {problemID}.pdf!")

def listContests() -> list[tuple[str, int]]:
    contests = []
    driver.get(f"{URL}/c#all")
    try:
        # table = driver.find_elements(By.XPATH, "//table[@class='contests']/tbody//tr")
        table = WebDriverWait(driver, 15).until(lambda d: d.find_elements(By.XPATH, "//table[@class='contests']/tbody//tr"))
    except TimeoutException:
        print("The contest list timed out")
        return []
    for tr in table:
        td = tr.find_elements(By.TAG_NAME, "td")[0]
        contestID = td.find_element(By.TAG_NAME, "a").get_attribute("href").split("/")[-1][1:]
        contests.append((td.text, contestID))
    return contests

if __name__=="__main__":
    driver.quit()
