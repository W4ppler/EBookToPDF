# EBookToPDF

---
This python script will convert these annoying Digi4School Books to PDFs.

## What this script does
The script will launch Chrome in headless mode
(u wont see any windows open) and visit the Digi4School Site. Then it checks if you
are already logged in, if not, it will ask you for ur login credentials. After a
successful login, you will be able to choose which ebook you want to convert.

---

## How it does that
The script uses the `selenium` package to interact with the Digi4School website by searching for elements using their
class names, IDs and XPATH's.
### Login
It firstly navigates to the login page and checks if you are already logged in, by looking
for the email field, if not it will ask you for your credentials.
### Presenting the ebooks
After logging in, it retrieves the list of available ebooks and allows you to select one.
### The actual conversion
It then clicks on the selected ebook and obtains the content by creating full page screenshots. These screenshots are then
cropped according to the ebook's dimensions. The crop box used in this process can be determined using various methods.
### Crop Box and different ebook types
Some ebooks can be hosted by other websites besides Digi4School, such as "Scook", "DigiBox", "BiBox" and "hpthek". If one
of your owned ebooks is hosted by someone else than Digi4School, you will be redirected to that website once you click
the ebook. After an ebook is selected, the script will determine the type of ebook by looking for key attributes. Once
the type is determined, the script will "prepare" the ebook to be converted to a PDF (selecting first page, determining
the crop box and closing pop ups). hpthek books and digibox books dont need extra handling, as they also use the digi4school's
book layout.

---

For further information on how a conversion is handled, please refer to the illustration below:
```text
1  main
2  ├── book_selection
3  │   └── check_book_type # looks for key elements on the page and returns -1, 0, 1, 2 or 3
4  │       ├── save_book_as_pdf_bibox
5  │       │   └── save_book_as_pdf_main
6  │       │       ├── crop_image           # crops the image using the crop box
7  │       │       └── images_are_identical # checks if img is identical to previous one,
8  │       │                                # if so -> end of book is reached
9  │       ├── save_book_as_pdf_digi4school
10 │       │   └── save_book_as_pdf_main
11 │       │       └── ... # same as line 6 and 7
12 │       ├── save_book_as_pdf_scook
13 │       │   └── save_book_as_pdf_main
14 │       │       └── ... # same as line 6 and 7
15 │       └── sub_book_selection
16 │           ├── save_book_as_pdf_bibox
17 │           │   └── save_book_as_pdf_main
18 │           │       └── ... # same as line 6 and 7
19 │           ├── save_book_as_pdf_digi4school
20 │           │   └── save_book_as_pdf_main
21 │           │       └── ... # same as line 6 and 7
22 │           └── save_book_as_pdf_scook
23 │               └── save_book_as_pdf_main
24 │                   └── ... # same as line 6 and 7
25 └── login
26     └── book_selection
27         └── check_book_type
28             └── same as above
```


## Requirements

*   Python 3.12.10
*   Google Chrome
    * Chrome download for [Linux](https://www.google.com/intl/en_uk/chrome/?platform=linux) and [Windows](https://www.google.com/chrome/)
*   The Python packages listed in `requirements.txt`.

## Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/W4ppler/EBookToPDF.git
    ```
2.  Navigate to the project directory:
    ```sh
    cd EBookToPDF
    ```
3.  Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
    
Alternatively, you can use the binary which you can find in the releases tab of this repository. There you will find a
precompiled windows executable, which you can run without installing Python or any dependencies.

## Usage

1.  Run the script from the project's root directory:
    ```sh
    python EBookToPDF.py
    ```
2.  The script will prompt you to enter the loading time between pages. You can press Enter to use the default value (0.5 seconds) or enter a higher value if you have a slow internet connection.
3.  You will be asked for your Digi4School email and password.
4.  The script will list all your available ebooks. Enter the number corresponding to the book you want to convert.
5.  If the selected book has multiple parts (sub-books), you will be prompted to choose one.
6.  The script will then proceed to capture each page, crop it, and convert it into a PDF file.
7.  The final PDF will be saved in a directory named after the book's title inside the `EBookToPDF` folder.

## Compatibility
I tested it on Windows 11 and Ubuntu 25.04, but it should work on any operating system that supports Python and has Google Chrome installed.

## AI Assistance
I used AI Autocomplete from the GitHub Copilot plugin for PyCharm. I wrote this readme myself, but asked Copilot in the end on what I
could improve. It suggested some changes, from which I applied some. There are parts in the script which are entirely written by AI, I only
asked it to give me ideas on how to fix some problems, if I had been stuck. 

## Disclaimer
This script does not constitute legal advice. Copyright laws and digital rights
management (DRM) regulations vary by jurisdiction and are complex. You are solely
responsible for ensuring your use of this script complies with all applicable local,
national, and international laws, including copyright law and any terms of service
or licensing agreements associated with Digi4School and its content.
