import time
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common import NoSuchElementException
from PIL import Image
from datetime import datetime


""""
TODO:
variable sleeps times (alle 100ms check of geladen)
eta / buch (progress bar)
dir für bücher
delete pics after conversion
OCR 
"""



def login(browser):
    email_field = browser.find_element(By.ID, "ion-input-0")
    passwd_field = browser.find_element(By.ID, "ion-input-1")

    # email = input("email: ")
    # passwd = input("password: ")

    email = "sdgsdffsd"
    passwd = "sdfsdfsdffsd"

    email_field.clear()
    email_field.send_keys(email)

    passwd_field.clear()
    passwd_field.send_keys(passwd)

    shadow_host = browser.find_element(By.CSS_SELECTOR, "ion-button[type='submit']")
    browser.execute_script("arguments[0].shadowRoot.querySelector('button[type=\"submit\"]').click();", shadow_host)

    sleep(2)

    if check_button_existence(By.ID, "ion-input-0", browser):
        print(datetime.now().strftime("%H:%M:%S") + " Login failed")
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

    selected_book = input(datetime.now().strftime("%H:%M:%S") + " Select a book: ")

    try:
        if books[int(selected_book)]:
            selected_book = books[int(selected_book)]
    except (ValueError, IndexError):
        print(datetime.now().strftime("%H:%M:%S") + " Book not found")
        return -1

    browser.find_element(By.XPATH, f"//h2[contains(text(), '{selected_book}')]").click()
    sleep(2)
    browser.switch_to.window(browser.window_handles[-1])

    print(datetime.now().strftime("%H:%M:%S") + f" Selected book: {selected_book}")

    return 0


def save_book_as_pdf(browser):
    browser.execute_script("document.body.style.zoom = 2.5") # with 2.5 zoom, the page is filling the whole viewport

    page = 1
    page_list = list()
    page_text_field = browser.find_element(By.ID, "txtPage")


    # initially sets the page to 1
    page_text_field.send_keys(page)
    page_text_field.send_keys(Keys.ENTER)

    sleep(3)

    page_list = []
    while not check_button_existence(By.CLASS_NAME, "ui-dialog", browser):
        browser.save_screenshot(f"{page}.png")
        print(datetime.now().strftime("%H:%M:%S") + " Saving page " + str(page))

        crop_image(f"{page}.png")
        print(datetime.now().strftime("%H:%M:%S") + " Cropped page " + str(page))

        page_list.append(f"{page}.png")
        page += 1
        page_text_field.send_keys(page)
        page_text_field.send_keys(Keys.ENTER)
        sleep(3)

    print(datetime.now().strftime("%H:%M:%S") + " Finished saving pages, now creating PDF...")

    images = []
    for f in page_list:
        images.append(Image.open(f).convert("RGB"))

    images[0].save("output.pdf", save_all=True, append_images=images[1:], resolution=300.0)

    print(datetime.now().strftime("%H:%M:%S") + " PDF created successfully.")


def crop_image(image):
    with Image.open(image) as img:
        cropped = img.crop((96, 128, 2368, 3343))
        cropped.save(f"{image}")


def main():
    options = Options()
    options.add_argument('--headless')
    options.add_argument(f'--window-size=2480,3508')

    with webdriver.Chrome(options=options) as browser:
        browser.get("https://digi4school.at/ebooks")

        sleep(2)

        if check_button_existence(By.ID, "ion-input-0", browser):
            login(browser)

        sleep(2)

        books = get_books(browser)

        while book_selection(browser, books) != 0:
            print(datetime.now().strftime("%H:%M:%S") + " Please select a valid book.")

        sleep(5)

        save_book_as_pdf(browser)




if __name__ == '__main__':
    main()
