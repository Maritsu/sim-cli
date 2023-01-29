from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from os import environ as env
env['MOZ_HEADLESS']='1'
driver = webdriver.Firefox() 
driver.get("http://127.0.0.1:8081")
assert ":/" in driver.title

solutionBox = driver.find_element(By.NAME, "solution")
solutionBox.send_keys("/home/bit/src/SpinningASCIIDonut/main.cpp")

sendBtn = driver.find_element(By.XPATH, "//input[@type='submit']")
sendBtn.click()

driver.save_screenshot('scr.png')
