from time import sleep
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

def login(browser):
    email_field = browser.find_element(By.ID, "ion-input-0")
    passwd_field = browser.find_element(By.ID, "ion-input-1")

    # email = input("email: ")
    # passwd = input("password: ")

    email = "notMyEmail@haha.at"
    passwd = "guessIt"

    email_field.clear()
    email_field.send_keys(email)

    passwd_field.clear()
    passwd_field.send_keys(passwd)

    shadow_host = browser.find_element(By.CSS_SELECTOR, "ion-button[type='submit']")
    browser.execute_script("arguments[0].shadowRoot.querySelector('button[type=\"submit\"]').click();", shadow_host)

    sleep(1)

    if check_button_existence(By.ID, "ion-input-0", browser):
        print("Login failed")
        browser.find_element(By.CLASS_NAME, "alert-button").click()
        login(browser)

def check_button_existence(locator_type, locator_value, browser):
    try:
        browser.find_element(locator_type, locator_value)
        return True
    except NoSuchElementException:
        return False

def get_books(browser):
    browser.execute_script("document.body.style.zoom='10%'")

    books = browser.find_elements(By.CLASS_NAME, "entry-heading")
    for book in books:
        print(book.text)



def main():
    with webdriver.Firefox() as browser:
        # browser.maximize_window()
        browser.get("https://digi4school.at/ebooks")

        sleep(2)

        if check_button_existence(By.ID, "ion-input-0", browser):
            login(browser)

        sleep(2)

        get_books(browser)


if __name__ == '__main__':
    main()

"""
browser.save_full_page_screenshot("imageToSave.png")
"""