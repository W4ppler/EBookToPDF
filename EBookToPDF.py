import os
from time import sleep

from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementNotInteractableException, MoveTargetOutOfBoundsException
from PIL import Image
from datetime import datetime
import numpy
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

""""
TODO:
next page popup
"""

mode_all = False
loading_time_between_pages = 0.5
bookname = "book.pdf"


def login(browser):
    """
    Logs the user into the digi4school.at website, by asking the user for their credentials.

    :param browser: Selenium WebDriver instance
    """
    email_field = browser.find_element(By.XPATH, "//*[@id=\"ion-input-0\"]")
    passwd_field = browser.find_element(By.XPATH, "//*[@id=\"ion-input-1\"]")

    email = input(datetime.now().strftime("%H:%M:%S") + " Email: ")
    passwd = input(datetime.now().strftime("%H:%M:%S") + " Password: ")

    # email = "dgcvbcvbmamamammmawasefsefsefsefsefesfsefsecom"  # for testing purposes, changed my email before every commit :)
    # passwd = "sergdhfgrewae"

    email_field.clear()
    email_field.send_keys(email)

    passwd_field.clear()
    passwd_field.send_keys(passwd)

    shadow_host = browser.find_element(By.XPATH,
                                       "//*[@id=\"main-content\"]/app-login/ion-content/div[1]/div/form/div[2]/ion-button[1]")
    browser.execute_script("arguments[0].shadowRoot.querySelector('button[type=\"submit\"]').click();", shadow_host)

    sleep(loading_time_between_pages + 1)

    if element_exists(By.XPATH, "//*[@id=\"ion-input-0\"]", browser):
        print(datetime.now().strftime("%H:%M:%S") + " Login failed")
        sleep(loading_time_between_pages)
        browser.find_element(By.CLASS_NAME, "alert-button").click()
        login(browser)


def element_exists(locator_type, locator_value, browser):
    """
    Checks if an element exists on the page.

    :param locator_type: Default Webdriver.find_element type, e.g. By.ID, By.CLASS_NAME, etc.
    :param locator_value: Default Webdriver.find_element value, e.g. "my_id", "my_class", etc.
    :param browser: Selenium WebDriver instance
    :return: Boolean value whether the element exists or not
    """
    try:
        browser.find_element(locator_type, locator_value)
        return True
    except NoSuchElementException:
        return False


def get_books(browser):
    """
    Obtains all book names from the site trough looking for the class "entry-heading" (in these classes, books are stored).

    :param browser: Selenium WebDriver instance
    :return: List of user owned books (Strings of the titles) and a list of book elements (Selenium WebElement objects)
    """

    browser.execute_script("document.body.style.zoom='10%'")  # Zooms very far out to render all books
    book_elements = browser.find_elements(By.CLASS_NAME, "entry-heading")

    book_names = list()
    for book in book_elements:
        book_names.append(book.text)

    return book_names, book_elements


def book_selection(browser, book_names, book_elements):
    """
    Firstly it lists all ur books, then it asks the user to select one.
    It also validates the input and switches to the newly opened book tab.

    :param browser: Selenium WebDriver instance
    :param book_names: for visual representation of the books
    :param book_elements: for interacting with the books (selecting them)
    :return: status code -1 if failed, 0 if successful
    """
    global bookname
    global mode_all

    for book in book_names:
        print("[" + str(book_names.index(book)) + "] " + book)
        # print([ord(c) for c in book])

    selected_book = input(
        datetime.now().strftime("%H:%M:%S") + " Select a book (enter 'all' to convert all owned books): ")

    if selected_book.lower() == 'all':
        mode_all = True
        print(datetime.now().strftime("%H:%M:%S") + " Selected mode: all books")
        save_all_books_as_pdf(browser, book_elements)
        return 0

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


def sub_book_selection(browser):
    """
    Only needed if there are sub_books (some books in Digi4School give u another list of options when u click on them).
    Firstly it lists all the sub_book items, then it asks the user to select one.
    It also validates the input and switches to the newly opened book tab.

    :param browser: Selenium WebDriver instance
    :return: status code -1 if failed, 0 if successful
    """
    global bookname
    book_elements = browser.find_elements(By.CLASS_NAME, "tx")
    books = list()

    for book_element in book_elements:
        if book_element.text:  # cause for some reason there are hundres of "tx" elements with no text
            books.append(book_element.text)

    for book in books:
        print("[" + str(books.index(book)) + "] " + book)

    selected_book = input(datetime.now().strftime("%H:%M:%S") + " Select a sub book: ")

    try:
        selected_book = books[int(selected_book)]
    except (ValueError, IndexError):
        print(datetime.now().strftime("%H:%M:%S") + " This sub book does not exist")
        return -1

    book_elements[books.index(selected_book)].click()
    bookname = os.path.join(bookname, selected_book.replace("/", "_"))
    sleep(loading_time_between_pages)
    browser.switch_to.window(browser.window_handles[-1])

    print(datetime.now().strftime("%H:%M:%S") + f" Selected sub book: {selected_book}")

    return 0


def crop_image(image, crop_box):
    """
    Crops the image based on the provided rectangle coordinates, cause the screenshots are full page screenshots.

    :param image: path to the image file
    :param crop_box: the associative array containing the coordinates of the rectangle to crop (left, top, right, bottom)
    """
    with Image.open(image) as img:
        cropped = img.crop((crop_box["left"] + 1, crop_box["top"] + 1, crop_box["right"], crop_box["bottom"]))
        cropped.save(f"{image}")


def images_are_identical(path1, path2):
    """
    Checks if two images are identical by comparing their pixel data. Needed for checking if the script reached the end of the book.
    If the images are identical, it returns True, thus the script stops saving pages.

    :param path1: path to the first image
    :param path2: path to the second image
    :return: True or False whether the images are identical or not
    """
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

    :param browser: Selenium WebDriver instance
    :return: -1 unknown and therefore unsupported book type, 0 sub_books are available, 1 Digi4School book (HPThek and
    digibox books use the same layout), 2 Scook book, 3 BiBox book
    """
    # print(browser.page_source)
    sleep(loading_time_between_pages+3)

    if element_exists(By.CLASS_NAME, "tx", browser):
        return 0
    elif element_exists(By.XPATH, "//*[@id=\"txtPage\"]", browser):
        return 1
    elif element_exists(By.XPATH, "//*[@id=\"page-product-viewer\"]", browser):
        return 2
    elif element_exists(By.XPATH,
                        "//*[@id=\"bbx\"]/app-root/app-book/div/mat-sidenav-container/mat-sidenav-content/app-double-page-view/div[1]/div[2]/app-book-page-viewer/div/app-book-gl/div/canvas",
                        browser) or element_exists(By.XPATH, "//*[@id=\"undefined\"]/app-book-gl/div/canvas", browser):
        return 3
    else:
        return -1


def save_book_as_pdf_core(browser, booktype, crop_box):
    """
    Creates dir for ebook, saves all pages as images, crops them using the crop_box and then creates a PDF from the
    images.

    :param browser: Selenium WebDriver instance
    :param booktype: 1, 2 or 3, depending on the book type (1 -> Digi4School book, 2 -> scook book, 3 -> bibox book)
    :param crop_box: associative array containing the coordinates of the rectangle to crop (left, top, right, bottom)
    """
    global bookname
    global mode_all
    page = 1
    page_list = []
    action = ActionChains(browser)

    action.move_by_offset(200, 200)
    action.perform()
    action.move_by_offset(-200, -200)
    action.perform()

    if not os.path.exists(bookname):
        os.makedirs(bookname)
        print(datetime.now().strftime("%H:%M:%S") + f" Created directory for book: {bookname}")

    # i = 0

    # while i < 3:  # only for testing
    while True:
        browser.save_screenshot(f"{bookname}" + "/" + f"{page}.png")

        crop_image(f"{bookname}" + "/" + f"{page}.png", crop_box)
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
        elif booktype == 3:
            browser.find_element(By.XPATH, "//*[@id=\"book-frame\"]/nav/div[2]/div/a[2]").click()
        else:
            print(datetime.now().strftime("%H:%M:%S") + " Unknown book type, cannot save pages")
            return


        # avoids "next page" popup that appears when hovering over "next page btn"

        action.move_by_offset(200, 200)
        action.perform()
        action.move_by_offset(-200, -200)
        action.perform()

        sleep(loading_time_between_pages)
        # i += 1
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
    """
    Special function for Digi4School books, as some books have a special layout and popups. After closing the popups,
    adjusting the zoom, selecting the first page, retrieving the crop_box using javascript and the elements of the DOM,
    it calls the main function to save the book as a PDF. This function "prepars" the book for saving.

    :param browser: Selenium WebDriver instance
    """
    # print(browser.page_source)

    if element_exists(By.CLASS_NAME, "tlypageguide_dismiss",
                      browser):  # usually appears when u open a book the first time
        print(datetime.now().strftime("%H:%M:%S") + " Infotour popup detected")
        try:
            browser.find_element(By.CLASS_NAME, "tlypageguide_dismiss").click()
            print(datetime.now().strftime("%H:%M:%S") + " Infotour popup closed")
        except ElementNotInteractableException:
            print(datetime.now().strftime("%H:%M:%S") + " Infotour popup isnt visible")

    if element_exists(By.ID, "routlineClose", browser):  # outline popup usually appears in german books
        print(datetime.now().strftime("%H:%M:%S") + " Detected outline popup")
        try:
            browser.find_element(By.ID, "routlineClose").click()
            print(datetime.now().strftime("%H:%M:%S") + " Closed outline popup")
        except ElementNotInteractableException:
            print(datetime.now().strftime("%H:%M:%S") + " Outline popup isnt visible")

    sleep(loading_time_between_pages)
    browser.find_element(By.ID, "btnFirst").click()
    sleep(loading_time_between_pages)

    if element_exists(By.ID, "btnZoomHeight", browser):
        browser.find_element(By.ID, "btnZoomHeight").click()

    crop_box = browser.execute_script(f"""
                    var el = document.getElementById('pg1Overlay');
                    var rect = el.getBoundingClientRect();
                    return rect;
                """)

    save_book_as_pdf_core(browser, 1, crop_box)


def save_book_as_pdf_bibox(browser):
    """
    Special function for bibox books, as some books have a special layout and popups. After closing the popups, selecting
    the first page and calculating the crop_box, it calls the main saving function to save the book as a PDF. This function
    prepares the book for saving.

    :param browser: Selenium WebDriver instance
    """
    wait = WebDriverWait(browser, 15)

    browser.set_window_size(2580, 3708)  # 3080 3708   2480 3508

    # switch to newer version of bibox
    if element_exists(By.ID, "flip-right", browser):
        print(datetime.now().strftime(
            "%H:%M:%S") + " Older version of BiBox is being used, switching to newer version...")
        browser.find_element(By.XPATH, "//*[@id=\"version-switch\"]").click()
        sleep(loading_time_between_pages)
        browser.find_element(By.XPATH,
                             "//*[@id=\"mat-mdc-dialog-2\"]/div/div/app-version-switch-modal/app-dialog-actions/div/div/button[2]").click()
        sleep(loading_time_between_pages)

    if element_exists(By.XPATH, "//*[@id=\"cdk-dialog-0\"]/bbx-notification-modal/app-standard-popup/div/div[3]/button",
                      browser):
        print(datetime.now().strftime("%H:%M:%S") + " Detected notification popup")
        try:
            browser.find_element(By.XPATH,
                                 "//*[@id=\"cdk-dialog-0\"]/bbx-notification-modal/app-standard-popup/div/div[3]/button").click()
            print(datetime.now().strftime("%H:%M:%S") + " Closed notification popup")
        except ElementNotInteractableException:
            print(datetime.now().strftime("%H:%M:%S") + " Notification popup isnt visible")

    # setting view to single page
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[@id=\"page-nav-layout\"]/app-toggle-item[1]/button/i")))
    browser.find_element(By.XPATH, "//*[@id=\"page-nav-layout\"]/app-toggle-item[1]/button/i").click()

    # selecting first page
    wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id=\"page-name\"]")))
    page_field = browser.find_element(By.XPATH, "//*[@id=\"page-name\"]")
    page_field.send_keys("1")
    page_field.send_keys(Keys.ENTER)

    sleep(loading_time_between_pages)

    # creating a screenshot to calculate the crop box
    browser.save_screenshot("temp.png")

    with Image.open("temp.png") as img:
        img = img.convert("RGB")

        img = img.crop((64, 24, 2502, 3506))
        img.save("temp_cropped.png")

    os.remove("temp.png")
    with Image.open("temp_cropped.png") as img:
        img_array = numpy.array(img)

        height, width, _ = img_array.shape
    os.remove("temp_cropped.png")

    top_border = 0
    while numpy.all(img_array[top_border, :] == (243, 245, 246)):
        top_border += 1

    left_border = 0
    while numpy.all(img_array[:, left_border] == (243, 245, 246)):
        left_border += 1

    right_border = width - 1
    while numpy.all(img_array[:, right_border] == (243, 245, 246)):
        right_border -= 1

    bottom_border = height - 1
    while numpy.all(img_array[bottom_border, :] == (243, 245, 246)):
        bottom_border -= 1

    # the borders are retrieved by checking when pixels are not white anymore
    # the +119 and +79 are offsets that are determined by the header and sidepanels
    crop_box = {"left": left_border + 119, "top": top_border + 79, "right": right_border + 64,
                "bottom": bottom_border + 24}

    save_book_as_pdf_core(browser, 3, crop_box)


def save_book_as_pdf_scook(browser):
    """
    Special function for scook books, as some books have a special layout and popups. After closing the popups, calculating
    the crop_box, selecting the first page and switching to the iframe, it calls the main saving function to save the book.
    This function prepares the book for saving.

    :param browser: Selenium WebDriver instance

    """
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

    sleep(loading_time_between_pages)

    crop_box = browser.execute_script(f"""
        var el = document.getElementsByClassName('annotations-drawable')[0]
        var rect = el.getBoundingClientRect();
        return rect;
    """)

    crop_box["left"] += iframe_rect["left"]
    crop_box["right"] += iframe_rect["left"]
    crop_box["top"] += iframe_rect["top"]
    crop_box["bottom"] += iframe_rect["top"]

    # first page
    browser.find_element(By.XPATH,
                         "/html/body/div[3]/div/div[2]/div/div/div/div[5]/div/div[2]/div[2]/button[1]").click()

    save_book_as_pdf_core(browser, 2, crop_box)


def save_all_books_as_pdf(browser, book_elements):
    """
    Still in development.

    :param browser:
    :param book_elements:
    :return:
    """

    global loading_time_between_pages
    global bookname

    for i in range(len(book_elements)):
        print(datetime.now().strftime("%H:%M:%S") + f" Saving item {book_elements[i].text}...")
        bookname = book_elements[i].text.replace("/", "_")
        book_elements[i].click()
        browser.switch_to.window(browser.window_handles[-1])

        sleep(loading_time_between_pages + 1)
        book_type = check_book_type(browser)
        if book_type == 0:
            print(datetime.now().strftime("%H:%M:%S") + " sub books detected, iterating trough all sub books...")
            sub_book_elements = browser.find_elements(By.CLASS_NAME, "tx")
            sub_books = list()

            for sub_book_element in sub_book_elements:
                if sub_book_element.text:  # because for some reason there are hundres of "tx" elements with no text
                    sub_books.append(sub_book_element)

            sub_book_list_page = browser.current_window_handle  # to switch back to the subbook list once a subbook is saved
            parent_book_name = bookname
            for sub_book in sub_books:
                print(datetime.now().strftime("%H:%M:%S") + f" Saving sub_book {sub_book.text}...")
                bookname = os.path.join(bookname, sub_book.text.replace("/", "_"))
                current_page = browser.current_window_handle
                sub_book.click()

                sleep(loading_time_between_pages)
                browser.switch_to.window(browser.window_handles[-1])
                sleep(loading_time_between_pages)

                if browser.current_window_handle == current_page:
                    print(datetime.now().strftime("%H:%M:%S") + " No new window opened, skipping...")
                    sleep(loading_time_between_pages)
                    continue

                sleep(loading_time_between_pages + 1)
                book_type = check_book_type(browser)
                if book_type == 1:
                    print(datetime.now().strftime("%H:%M:%S") + " Digi4School book detected, saving as PDF...")
                    save_book_as_pdf_digi4school(browser)
                elif book_type == 2:
                    print(datetime.now().strftime("%H:%M:%S") + " Scook book detected, saving as PDF...")
                    save_book_as_pdf_scook(browser)
                elif book_type == 3:
                    print(datetime.now().strftime("%H:%M:%S") + " BiBox book detected, saving as PDF...")
                    save_book_as_pdf_bibox(browser)
                else:
                    print(datetime.now().strftime("%H:%M:%S") + " Unknown book type detected, skipping...")

                bookname = parent_book_name
                browser.close()
                print(datetime.now().strftime("%H:%M:%S") + " Closed sub book tab.")
                browser.switch_to.window(sub_book_list_page)
                sleep(loading_time_between_pages)

            browser.switch_to.window(browser.window_handles[0])


        elif book_type == 1:
            print(datetime.now().strftime("%H:%M:%S") + " Digi4School book detected, saving as PDF...")
            save_book_as_pdf_digi4school(browser)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        elif book_type == 2:
            print(datetime.now().strftime("%H:%M:%S") + " Scook book detected, saving as PDF...")
            save_book_as_pdf_scook(browser)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        elif book_type == 3:
            print(datetime.now().strftime("%H:%M:%S") + " BiBox book detected, saving as PDF...")
            save_book_as_pdf_bibox(browser)
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
        else:
            print(datetime.now().strftime("%H:%M:%S") + " Unknown book type detected, skipping...")
            sleep(loading_time_between_pages)
            browser.close()
            sleep(loading_time_between_pages)
            browser.switch_to.window(browser.window_handles[0])
            sleep(loading_time_between_pages)


def main():
    global loading_time_between_pages
    global mode_all
    options = Options()

    options.add_argument('--headless')
    options.add_argument(f'--window-size=3080,3708')  # 2480,3508
    options.add_argument('--log-level=3')

    with webdriver.Chrome(options=options) as browser:
        wait = WebDriverWait(browser, 15)
        sleep(5)  # to avoid the warning obstructing the input()

        print("""  
                   ███████╗██████╗  ██████╗  ██████╗ ██╗  ██╗                                    
                   ██╔════╝██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝                                     
                   █████╗  ██████╔╝██║   ██║██║   ██║█████╔╝                                     
                   ██╔══╝  ██╔══██╗██║   ██║██║   ██║██╔═██╗                                      
                   ███████╗██████╔╝╚██████╔╝╚██████╔╝██║  ██╗                                     
                   ╚══════╝╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝                             
                           XX                                                      
                         XXXX                                                      
                        XXXX                ███████████  ██████████   ███████████  
                       XXXX        XXX      ░░███░░░░░███░░███░░░░███ ░░███░░░░░░█ 
                      XXXX        XXXXX      ░███    ░███ ░███   ░░███ ░███   █ ░  
                     XXXXXX        XXXXX     ░██████████  ░███    ░███ ░███████    
                    XXXXXXXXXXXXXXXXXXXXX    ░███░░░░░░   ░███    ░███ ░███░░░█    
                     XXXXXXXXXXXXXXXXXXXX    ░███         ░███    ███  ░███  ░     
                                   XXXXX     █████        ██████████   █████       
                                  XXXXX     ░░░░░        ░░░░░░░░░░   ░░░░░        
                                   XXX                                             """)

        print("""                                                  
                ██╗    ██╗██╗  ██╗██████╗ ██████╗ ██╗     ███████╗██████╗ 
                ██║    ██║██║  ██║██╔══██╗██╔══██╗██║     ██╔════╝██╔══██╗
                ██║ █╗ ██║███████║██████╔╝██████╔╝██║     █████╗  ██████╔╝
                ██║███╗██║╚════██║██╔═══╝ ██╔═══╝ ██║     ██╔══╝  ██╔══██╗
                ╚███╔███╔╝     ██║██║     ██║     ███████╗███████╗██║  ██║
                 ╚══╝╚══╝      ╚═╝╚═╝     ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝

            """)

        while True:
            user_input = input(
                datetime.now().strftime(
                    "%H:%M:%S") + " Enter loading time between pages in seconds. By default this is set to 0.5. If you have \n"
                                  "a slower internet connection, you may prefer a higher value. If the \"next page\" pop ups on each \n"
                                  "page annoy you, you may also prefer a higher value. \n"
                                  "Seconds: ")
            if user_input == "":
                break
            try:
                loading_time_between_pages = float(user_input)
                break
            except ValueError:
                print(datetime.now().strftime("%H:%M:%S") + " Please enter a valid number.")

        browser.get("https://digi4school.at/overview")

        wait.until(EC.any_of(
            EC.visibility_of_element_located((By.XPATH, "//*[@id=\"ion-input-0\"]")),
            EC.visibility_of_element_located((By.CLASS_NAME, "entry-heading")),
        ))

        if element_exists(By.ID, "ion-input-0", browser):
            login(browser)

        book_names, book_elements = get_books(browser)

        while book_selection(browser, book_names, book_elements) != 0:
            print(datetime.now().strftime("%H:%M:%S") + " Please select a valid book.")

        if mode_all:
            print(datetime.now().strftime("%H:%M:%S") + " Finished saving all books. Press Enter to exit.")
            input()
            return

        sleep(loading_time_between_pages + 1)
        book_type = check_book_type(
            browser)  # 0 -> sub_books, 1 -> Digi4School book (hpthek and digibox books are also compatible), 2 -> scook, 3 -> bibox, None -> unknown book type

        if book_type == 0:
            print(datetime.now().strftime("%H:%M:%S") + " sub_books detected.")
            while sub_book_selection(browser) != 0:
                print(datetime.now().strftime("%H:%M:%S") + " Please select a valid sub_book.")

            sleep(loading_time_between_pages + 1)
            book_type = check_book_type(browser)

        if book_type == 1:
            print(datetime.now().strftime("%H:%M:%S") + " Digi4School book detected.")
            save_book_as_pdf_digi4school(browser)
        elif book_type == 2:
            print(datetime.now().strftime("%H:%M:%S") + " Scook book detected.")
            save_book_as_pdf_scook(browser)
        elif book_type == 3:
            print(datetime.now().strftime("%H:%M:%S") + " BiBox book detected.")
            save_book_as_pdf_bibox(browser)
        else:
            print(datetime.now().strftime("%H:%M:%S") + " Unknown book type detected.")
            print(datetime.now().strftime(
                "%H:%M:%S") + " This issue could also be caused when a page takes too long to load, try increasing the loading time between pages.")
            print(datetime.now().strftime("%H:%M:%S") + " Exiting...")
            sleep(1)
            return

        print("Press Enter to exit")
        input()


if __name__ == '__main__':
    main()
