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

URL = "https://sim.13lo.pl"
# URL = "http://127.0.0.1:8081"
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
    print("Sending submission... ", end="")
    try:
        WebDriverWait(driver, 60).until(lambda d: d.find_element(By.XPATH, "//div[@class='spinner']"))
    except TimeoutException:
        print("Timed out (Not even the spinner loaded.. wow)")
        return
    try:
        # Wait until error box appears or URL changes to submission
        WebDriverWait(driver, 60).until(EC.any_of(lambda d: d.find_element(By.XPATH, "//span[@class='oldloader-info error']", EC.url_changes(f"{URL}/s/3621"))))
    except TimeoutException:
        print("Timed out")
        return

    url = driver.current_url
    if "/s/" in url:
        subID = int(url.split('/')[-1].split('#')[0])
        print(f"Done!\nSubmission ID: {subID}")
    else:
        # Submission failed
        errorSpan = driver.find_element(By.XPATH, "//span[@class='oldloader-info error']")
        print(f"\n{errorSpan.text}")

def getStatementURL(problemID:int) -> str:
    return f"{URL}/api/download/statement/contest/p{problemID}/"

def openStatement(problemID:int) -> None:
    from subprocess import call
    call(["xdg-open", getStatementURL(problemID)])

def downloadStatement(problemID:int) -> None:
    from pathlib import Path
    response = requests.get(getStatementURL(problemID), stream=True)
    with Path(f"{problemID}.pdf") as f:
        f.write_bytes(response.content)
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

def displayContests() -> None:
    contestList = listContests()
    for contest in contestList:
        print(f"[ID: {contest[1]}] {contest[0]}")

def listContestRounds(contestID:int) -> list[tuple[str, int]]:
    rounds = []
    driver.get(f"{URL}/c/c{contestID}#dashboard")
    try:
        # Either the list appears, or an error box appears.
        # REMINDER: locators should be wrapped in (), e.g. (By.FOO, "bar") instead of By.FOO, "bar"
        roundsList = WebDriverWait(driver, 15).until(EC.any_of(EC.presence_of_element_located((By.XPATH, "//div[@class='rounds']")), EC.presence_of_element_located((By.XPATH, "//span[@class='oldloader-info error']"))))
    except TimeoutException:
        print("The contest dashboard timed out")
        return []
    if roundsList.tag_name == "span":
        # TODO: Replace this print with an actual parser for the error message
        print(f"{roundsList.text}")
        return []

    for round in roundsList.find_elements(By.CLASS_NAME, "round"):
        a = round.find_element(By.TAG_NAME, "a")
        roundSpan = a.find_element(By.TAG_NAME, "span")
        roundID = int(a.get_attribute("href").split("/")[-1][1:])
        rounds.append((roundSpan.text, roundID))
    return rounds

def listRoundProblems(roundID:int) -> list[tuple[str, int]]:
    problems = []
    driver.get(f"{URL}/c/r{roundID}#dashboard")
    try:
        # Same situation as in listContestRounds()
        problemList = WebDriverWait(driver, 15).until(EC.any_of(EC.presence_of_element_located((By.XPATH, "//div[@class='round']")), EC.presence_of_element_located((By.XPATH, "//span[@class='oldloader-info error']"))))
    except TimeoutException:
        print("The contest dashboard timed out")
        return []
    if problemList.tag_name == "span":
        # TODO: Replace this print with an actual parser for the error message
        print(f"{problemList.text}")
        return []

    skippedTitle = False
    for problem in problemList.find_elements(By.TAG_NAME, "a"):
        if not skippedTitle:
            skippedTitle = True
            continue
        problemSpan = problem.find_element(By.TAG_NAME, "span")
        problemID = int(problem.get_attribute("href").split("/")[-1][1:])
        problems.append((problemSpan.text, problemID))
    return problems

if __name__=="__main__":
    driver.quit()
