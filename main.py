from time import sleep
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

def login(browser):
    email_field = browser.find_element(By.ID, "email")
    passwd_field = browser.find_element(By.ID, "password")

    email = input("email: ")
    passwd = input("password: ")

    email_field.clear()
    email_field.send_keys(email)
    passwd_field.clear()
    passwd_field.send_keys(passwd)
    browser.find_element(By.XPATH, "//button[contains(text(), 'Anmelden')]").click()
    sleep(3)
    if browser.find_element(By.ID, "email"):
        print("Login failed")
        browser.find_element(By.CLASS_NAME, "ui-button ui-corner-all ui-widget ui-button-icon-only ui-dialog-titlebar-close").click()
        login(browser)

def check_button_existing(locator_type, locator_value):
    try:
        browser.find_element(locator_type, locator_value)
        return True
    except NoSuchElementException:
        return False


browser = webdriver.Firefox()
browser.maximize_window()
browser.get("https://digi4school.at/ebooks")

if check_button_existing(By.ID, "email"):
    login(browser)


browser.quit()

"""
browser.save_full_page_screenshot("imageToSave.png")
"""