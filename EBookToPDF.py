from time import sleep
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

def login(browser):
    email_field = browser.find_element(By.ID, "ion-input-0")
    passwd_field = browser.find_element(By.ID, "ion-input-1")

    # email = input("email: ")
    # passwd = input("password: ")

    email = "stillnot@myemail.nz"
    passwd = "password123"

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
    browser.execute_script("document.body.style.zoom='10%'") # Zooms very far out to render all books
    book_names = browser.find_elements(By.CLASS_NAME, "entry-heading")

    books = list()
    for book in book_names:
        books.append(book.text)

    browser.execute_script("document.body.style.zoom='100%'")
    return books


def book_selection(browser, books):
    for book in books:
        print("[" + str(books.index(book)) + "] " + book)

    selected_book = input("Select a book: ")

    try:
        if books[int(selected_book)]:
            selected_book = books[int(selected_book)]
    except (ValueError, IndexError):
        print("Book not found")
        return -1

    browser.find_element(By.XPATH, f"//h2[contains(text(), '{selected_book}')]").click()
    sleep(0.5)
    browser.switch_to.window(browser.window_handles[-1])

    print(f"Selected book: {selected_book}")

    return 0


def save_book_as_pdf(browser):
    browser.find_element(By.ID, "btnFirst").click()

def main():
    with webdriver.Firefox() as browser:
        browser.get("https://digi4school.at/ebooks")

        sleep(2)

        if check_button_existence(By.ID, "ion-input-0", browser):
            login(browser)

        sleep(1)

        books = get_books(browser)

        while book_selection(browser, books) != 0:
            print("Please select a valid book.")

        sleep(0.5)

        save_book_as_pdf(browser)

        sleep(60)


if __name__ == '__main__':
    main()

"""
browser.save_full_page_screenshot("imageToSave.png")
"""