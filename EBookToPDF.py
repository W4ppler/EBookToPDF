import os
from logging import setLoggerClass
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementNotInteractableException
from PIL import Image
from datetime import datetime
import numpy
from selenium.webdriver.support.wait import WebDriverWait

""""
TODO:
compatible with all books?
english books
    timeout for materials and audios
infotour
next page popup on each page
convert all books
digibox books
conversion to xpath
documentation
webdriverwait
"""

loading_time_between_pages = 1
bookname = "book.pdf"


def login(browser):
    email_field = browser.find_element(By.ID, "ion-input-0")
    passwd_field = browser.find_element(By.ID, "ion-input-1")

    # email = input("email: ")
    # passwd = input("password: ")

    email = "awdawd.awdawd@awdawd.com"
    passwd = "awdawdadwawddaw"

    email_field.clear()
    email_field.send_keys(email)

    passwd_field.clear()
    passwd_field.send_keys(passwd)

    shadow_host = browser.find_element(By.CSS_SELECTOR, "ion-button[type='submit']")
    browser.execute_script("arguments[0].shadowRoot.querySelector('button[type=\"submit\"]').click();", shadow_host)

    sleep(loading_time_between_pages)

    if element_exists(By.ID, "ion-input-0", browser):
        print(datetime.now().strftime("%H:%M:%S") + " Login failed")
        browser.find_element(By.CLASS_NAME, "alert-button").click()
        login(browser)


def element_exists(locator_type, locator_value, browser):
    try:
        browser.find_element(locator_type, locator_value)
        return True
    except NoSuchElementException:
        return False


def get_books(browser):
    browser.execute_script("document.body.style.zoom='10%'")  # Zooms very far out to render all books
    book_elements = browser.find_elements(By.CLASS_NAME, "entry-heading")

    book_names = list()
    for book in book_elements:
        book_names.append(book.text)

    return book_names, book_elements


def book_selection(browser, book_names, book_elements):
    global bookname

    for book in book_names:
        print("[" + str(book_names.index(book)) + "] " + book)
        # print([ord(c) for c in book])

    selected_book = input(datetime.now().strftime("%H:%M:%S") + " Select a book: ")

    if selected_book.lower() == 'all':
        pass  # todo

    try:
        selected_book = book_names[int(selected_book)]
    except (ValueError, IndexError):
        print(datetime.now().strftime("%H:%M:%S") + " Book not found")
        return -1

    book_elements[book_names.index(selected_book)].click()
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
        if book_element.text:  # cause for some reason there are thousands of "tx" elements with no text
            books.append(book_element.text)

    for book in books:
        print("[" + str(books.index(book)) + "] " + book)

    selected_book = input(datetime.now().strftime("%H:%M:%S") + " Select a subbook: ")

    try:
        selected_book = books[int(selected_book)]
    except (ValueError, IndexError):
        print(datetime.now().strftime("%H:%M:%S") + " This subbook does not exist")
        return -1

    book_elements[books.index(selected_book)].click()
    bookname = os.path.join(bookname, selected_book.replace("/", "_"))
    sleep(loading_time_between_pages)
    browser.switch_to.window(browser.window_handles[-1])

    print(datetime.now().strftime("%H:%M:%S") + f" Selected subbook: {selected_book}")

    return 0


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


def check_book_type(browser):
    """
    Check the book type based on the elements present in the browser.
    None -> unknown book type
    0 -> subbooks are available
    1 -> digi4school book (hpthek and digibox books use the same layout)
    2 -> scook book
    3 -> bibox book
    :param browser:
    :return:
    """
    if element_exists(By.CLASS_NAME, "tx", browser):
        return 0
    elif element_exists(By.XPATH, "//*[@id=\"txtPage\"]", browser):
        return 1
    elif element_exists(By.XPATH, "//*[@id=\"page-product-viewer\"]", browser):
        return 2
    elif element_exists(By.XPATH, "//*[@id=\"version-switch\"]", browser):
        return 3
    else:
        return None


def save_book_as_pdf_main(browser, booktype, div_rect):
    page = 1
    global bookname

    if not os.path.exists(bookname):
        os.makedirs(bookname)
        print(datetime.now().strftime("%H:%M:%S") + f" Created directory for book: {bookname}")

    i = 0
    page_list = []

    # while i < 5:  # only for testing
    while True:
        browser.save_screenshot(f"{bookname}" + "/" + f"{page}.png")

        crop_image(f"{bookname}" + "/" + f"{page}.png", div_rect)
        print(datetime.now().strftime("%H:%M:%S") + " Saved and cropped page " + str(page))

        page_list.append(f"{bookname}" + "/" + f"{page}.png")

        if len(page_list) > 1:
            if images_are_identical(page_list[-2], page_list[-1]):
                os.remove(page_list[-1])
                page_list.pop()
                break

        if booktype == 1:
            browser.find_element(By.ID, "btnNext").click()
        elif booktype == 2:
            browser.find_element(By.XPATH,
                                 "//*[@id=\"content-0\"]/div/div/div/div[5]/div/div[2]/div[2]/button[3]").click()

        sleep(loading_time_between_pages / 2)
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


def save_book_as_pdf_digi4school(browser):
    # print(browser.page_source)

    if element_exists(By.ID, "routlineClose", browser):  # outline popup usually appears in german books
        print(datetime.now().strftime("%H:%M:%S") + " Detected outline popup")
        try:
            browser.find_element(By.ID, "routlineClose").click()
            print(datetime.now().strftime("%H:%M:%S") + " Closed outline popup")
        except ElementNotInteractableException:
            print(datetime.now().strftime("%H:%M:%S") + " Outline popup isnt visible")

    if element_exists(By.CLASS_NAME, "tlypageguide_dismiss",
                      browser):  # usually appears when u open a book the first time
        print(datetime.now().strftime("%H:%M:%S") + " Infotour popup detected")
        try:
            browser.find_element(By.CLASS_NAME, "tlypageguide_dismiss").click()
            print(datetime.now().strftime("%H:%M:%S") + " Infotour popup closed")
        except ElementNotInteractableException:
            print(datetime.now().strftime("%H:%M:%S") + " Infotour popup isnt visible")

    browser.find_element(By.ID, "btnFirst").click()
    sleep(loading_time_between_pages)

    if element_exists(By.ID, "btnZoomHeight", browser):
        browser.find_element(By.ID, "btnZoomHeight").click()

    div_rect = browser.execute_script(f"""
                    var el = document.getElementById('pg1Overlay');
                    var rect = el.getBoundingClientRect();
                    return rect;
                """)

    save_book_as_pdf_main(browser, 1, div_rect)


"""
def save_book_as_pdf_bibox(browser):
    \"""
    This function is not finished yet, dont use it.
    :param browser:
    :return:
    \"""

    # switch to newer version of bibox
    if element_exists(By.ID, "flip-right", browser):
        print(datetime.now().strftime("%H:%M:%S") + " Older version of BiBox is being used, switching to newer version...")
        browser.find_element(By.XPATH, "//*[@id=\"version-switch\"]").click()
        sleep(loading_time_between_pages/2)
        browser.find_element(By.XPATH, "//*[@id=\"mat-mdc-dialog-2\"]/div/div/app-version-switch-modal/app-dialog-actions/div/div/button[2]").click()

    # setting view to single page
    browser.find_element(By.XPATH, "//*[@id=\"page-nav-layout\"]/app-toggle-item[1]/button").click()

    # selecting first page
    browser.find_element(By.XPATH, "//*[@id=\"page-name\"]").send_keys("1").send_keys(Keys.ENTER)

    save_book_as_pdf_main(browser, 3)

    # todo: bibox books are not supported yet, thus this function is never called
"""


def save_book_as_pdf_scook(browser):
    sleep(loading_time_between_pages)  # scook books take more time to load

    # closing annoying popups
    if element_exists(By.XPATH,
                      "//*[@id=\"unity-veritas-product-viewer-component-67076960\"]/div[1]/aside/div[1]/div[1]/span",
                      browser):
        print(datetime.now().strftime("%H:%M:%S") + " Detected chapter view panel")
        try:
            browser.find_element(By.XPATH,
                                 "//*[@id=\"unity-veritas-product-viewer-component-67076960\"]/div[1]/aside/div[1]/div[1]/span").click()
            print(datetime.now().strftime("%H:%M:%S") + " Closed chapter view panel")
        except ElementNotInteractableException:
            print(datetime.now().strftime("%H:%M:%S") + " Chapter view panel isnt visible")

    iframe = browser.find_elements(By.TAG_NAME, "iframe")[0]

    iframe_rect = browser.execute_script(f"""
        var el = document.getElementsByClassName('book-frame')[0]
        var rect = el.getBoundingClientRect();
        return rect;
    """)

    browser.switch_to.frame(iframe)

    div_rect = browser.execute_script(f"""
        var el = document.getElementsByClassName('annotations-drawable')[0]
        var rect = el.getBoundingClientRect();
        return rect;
    """)

    div_rect["left"] += iframe_rect["left"]
    div_rect["right"] += iframe_rect["left"]
    div_rect["top"] += iframe_rect["top"]
    div_rect["bottom"] += iframe_rect["top"]

    # first page
    browser.find_element(By.XPATH,
                         "/html/body/div[3]/div/div[2]/div/div/div/div[5]/div/div[2]/div[2]/button[1]").click()

    save_book_as_pdf_main(browser, 2, div_rect)


def main():
    global loading_time_between_pages
    options = Options()
    options.add_argument('--headless')
    options.add_argument(f'--window-size=3000,3808')  # 2480,3508

    with webdriver.Chrome(options=options) as browser:
        while True:
            user_input = input(
                datetime.now().strftime(
                    "%H:%M:%S") + " Enter loading time between pages (in seconds, default is 1, slower internet - higher, faster internet - smaller): ")
            if user_input == "":
                loading_time_between_pages = 1
                break
            try:
                loading_time_between_pages = float(user_input)
                break
            except ValueError:
                print(datetime.now().strftime("%H:%M:%S") + " Please enter a valid number.")

        browser.get("https://digi4school.at/ebooks")

        sleep(loading_time_between_pages)

        if element_exists(By.ID, "ion-input-0", browser):
            login(browser)

        book_names, book_elements = get_books(browser)

        while book_selection(browser, book_names, book_elements) != 0:
            print(datetime.now().strftime("%H:%M:%S") + " Please select a valid book.")

        sleep(loading_time_between_pages)
        book_type = check_book_type(
            browser)  # 0 -> subbooks, 1 -> digi4school book (hpthek books are also compatible), 2 -> scook, 3 -> bibox, None -> unknown book type
        sleep(loading_time_between_pages)

        if book_type == 0:
            print(datetime.now().strftime("%H:%M:%S") + " Subbooks detected.")
            while subbook_selection(browser) != 0:
                print(datetime.now().strftime("%H:%M:%S") + " Please select a valid subbook.")
            book_type = check_book_type(browser)

        if book_type == 1:
            print(datetime.now().strftime("%H:%M:%S") + " Digi4School book detected.")
            save_book_as_pdf_digi4school(browser)
        elif book_type == 2:
            print(datetime.now().strftime("%H:%M:%S") + " Scook book detected.")
            save_book_as_pdf_scook(browser)
        elif book_type == 3:
            print(datetime.now().strftime(
                "%H:%M:%S") + " BiBox book detected. BiBox books are not supported, therefore exiting...")
            return
        else:
            print(datetime.now().strftime("%H:%M:%S") + " Unknown book type detected. Exiting...")
            return


if __name__ == '__main__':
    main()
