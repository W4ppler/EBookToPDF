import os
from logging import setLoggerClass
from time import sleep

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementNotInteractableException
from PIL import Image
from datetime import datetime
import numpy

""""
TODO:
compatible with all books?
english books
    timeout for materials and audios
infotour
next page popup on each page
convert all books
"""

loading_time_between_pages = 1
bookname = "book.pdf"


def login(browser):
    email_field = browser.find_element(By.ID, "ion-input-0")
    passwd_field = browser.find_element(By.ID, "ion-input-1")

    # email = input("email: ")
    # passwd = input("password: ")

    email = "sdrgrgddrgdrsef"
    passwd = "sdrgdrgdgrsef"

    email_field.clear()
    email_field.send_keys(email)

    passwd_field.clear()
    passwd_field.send_keys(passwd)

    shadow_host = browser.find_element(By.CSS_SELECTOR, "ion-button[type='submit']")
    browser.execute_script("arguments[0].shadowRoot.querySelector('button[type=\"submit\"]').click();", shadow_host)

    sleep(loading_time_between_pages)

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
    browser.execute_script("document.body.style.zoom='10%'")  # Zooms very far out to render all books
    books = browser.find_elements(By.CLASS_NAME, "entry-heading")

    book_names = list()
    for book in books:
        book_names.append(book.text)

    return book_names


def book_selection(browser, books):
    global bookname

    for book in books:
        print("[" + str(books.index(book)) + "] " + book)

    selected_book = input(datetime.now().strftime("%H:%M:%S") + " Select a book: ")

    if selected_book.lower() == 'all':
        pass

    try:
        selected_book = books[int(selected_book)]
    except (ValueError, IndexError):
        print(datetime.now().strftime("%H:%M:%S") + " Book not found")
        return -1

    browser.find_element(By.XPATH, f'//h2[contains(text(), "{selected_book}")]').click()
    bookname = selected_book.replace("/", "_")
    sleep(loading_time_between_pages)
    browser.switch_to.window(browser.window_handles[-1])

    print(datetime.now().strftime("%H:%M:%S") + f" Selected book: {selected_book}")
    return 0



def subbook_selection(browser):
    global bookname
    book_elements = browser.find_elements(By.CLASS_NAME, "tx")
    books = list()

    for book_element in book_elements:
        if book_element.text:
            books.append(book_element.text)

    for book in books:
        print("[" + str(books.index(book)) + "] " + book)

    selected_book = input(datetime.now().strftime("%H:%M:%S") + " Select a subbook: ")

    try:
        selected_book = books[int(selected_book)]
    except (ValueError, IndexError):
        print(datetime.now().strftime("%H:%M:%S") + " This subbook does not exist")
        return -1

    browser.find_element(By.XPATH, f"//h1[contains(text(), '{selected_book}')]").click()
    bookname = os.path.join(bookname, selected_book.replace("/", "_"))
    sleep(loading_time_between_pages)
    browser.switch_to.window(browser.window_handles[-1])

    print(datetime.now().strftime("%H:%M:%S") + f" Selected subbook: {selected_book}")

    return 0


def save_book_as_pdf(browser):
    global bookname
    page = 1

    if check_button_existence(By.ID, "routlineClose", browser):
        print(datetime.now().strftime("%H:%M:%S") + " Detected outline popup")
        try:
            browser.find_element(By.ID, "routlineClose").click()
            print(datetime.now().strftime("%H:%M:%S") + " Closed outline popup")
        except ElementNotInteractableException:
            print(datetime.now().strftime("%H:%M:%S") + " Outline popup isnt visible")

    browser.find_element(By.ID, "btnFirst").click()

    sleep(loading_time_between_pages)

    if check_button_existence(By.ID, "btnZoomHeight", browser):
        browser.find_element(By.ID, "btnZoomHeight").click()
    else:
        browser.execute_script(f"document.body.style.zoom = 2")


    div_rect = browser.execute_script(f"""
        var el = document.getElementById('pg1Overlay');
        var rect = el.getBoundingClientRect();
        return rect;
    """)

    if not os.path.exists(bookname):
        os.makedirs(bookname)
        print(datetime.now().strftime("%H:%M:%S") + f" Created directory for book: {bookname}")

    i = 0
    page_list = []
    while i < 5: # only for testing

    # while True:
        browser.save_screenshot(f"{bookname}" + "/" + f"{page}.png")

        crop_image(f"{bookname}" + "/" + f"{page}.png", div_rect)
        print(datetime.now().strftime("%H:%M:%S") + " Saved and cropped page " + str(page))

        page_list.append(f"{bookname}" + "/" + f"{page}.png")

        if len(page_list) > 1:
            if images_are_identical(page_list[-2], page_list[-1]):
                os.remove(page_list[-1])
                page_list.pop()
                break

        browser.find_element(By.ID, "btnNext").click()

        sleep(loading_time_between_pages/2)
        i += 1

        page += 1


    print(datetime.now().strftime("%H:%M:%S") + " Finished saving pages, now creating PDF...")

    images = []
    for f in page_list:
        images.append(Image.open(f).convert("RGB"))

    pdf_filename = os.path.basename(bookname)
    images[0].save(f"{bookname}/{pdf_filename}.pdf", save_all=True, append_images=images[1:], resolution=300.0)

    print(datetime.now().strftime("%H:%M:%S") + " PDF created successfully.")

    for i in page_list:
        os.remove(i)


def crop_image(image, div_rect):
    with Image.open(image) as img:
        cropped = img.crop((div_rect["left"] + 1, div_rect["top"] + 1, div_rect["right"], div_rect["bottom"]))
        cropped.save(f"{image}")




def images_are_identical(path1, path2):
    if not os.path.exists(path1) or not os.path.exists(path2):
        return False

    with Image.open(path1) as img1, Image.open(path2) as img2:
        if img1.size != img2.size:
            return False
        arr1 = numpy.array(img1)
        arr2 = numpy.array(img2)
        return numpy.array_equal(arr1, arr2)


def main():
    global loading_time_between_pages
    options = Options()
    options.add_argument('--headless')
    options.add_argument(f'--window-size=3000,3608')  # 2480,3508

    with webdriver.Chrome(options=options) as browser:
        while True:
            user_input = input(
                "Enter loading time between pages (in seconds, default is 1, slower internet - higher, faster internet - smaller): ")
            if user_input == "":
                loading_time_between_pages = 1
                break
            try:
                loading_time_between_pages = float(user_input)
                break
            except ValueError:
                print("Please enter a valid number.")

        browser.get("https://digi4school.at/ebooks")

        sleep(loading_time_between_pages)

        if check_button_existence(By.ID, "ion-input-0", browser):
            login(browser)

        sleep(loading_time_between_pages)

        books = get_books(browser)

        while book_selection(browser, books) != 0:
            print(datetime.now().strftime("%H:%M:%S") + " Please select a valid book.")

        sleep(loading_time_between_pages)

        if check_button_existence(By.CLASS_NAME, "tx", browser):
            subbook_selection(browser)

        save_book_as_pdf(browser)


if __name__ == '__main__':
    main()
