import sys
import os
import re
import time
from idlelib.iomenu import encoding
from typing import final
import json
import requests

from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chromium.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from urllib3.exceptions import MaxRetryError

if getattr(sys, 'Frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath("__file__"))

source_file_path = os.path.join(base_path,'source_html')


AUDIT_URL = "https://audit.portico.org/Portico/login.html"
MODE = "LOAD" ## LOAD/SCRAPE
provider_page_source = None

ISBN_FOUND_UNDER_CS = []
ISBN_NOT_FOUND_UNDER_CS = []
ISBN_FOUND_UNDER_OTHER_PROVIDER = []

class BookCompletenessCheckerBot:
    def __init__(self, username, password):
        self.chrome_option = webdriver.ChromeOptions()
        self.chrome_option.add_argument("--headless")
        # self.chrome_option.add_argument("start-maximized")
        self.chrome_option.add_argument("--window-size=1920x1080")
        self.chrome_option.add_argument("user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'")
        self.chrome_option.add_argument("--disable-blink-features=AutomationControlled")

        self.chrome_option.add_experimental_option("detach", True)
        self.chrome_option.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.chrome_option.add_experimental_option('useAutomationExtension', False)

        self.driver  = webdriver.Chrome(options=self.chrome_option)
        self.wait  = WebDriverWait(self.driver, timeout=20)
        self.driver.get(AUDIT_URL)
        self.login_audit_site(username, password)



    def login_audit_site(self, username, password):
        username_field = self.driver.find_element(by=By.XPATH, value='//*[@id="username"]')
        username_field.send_keys(username)

        password_field = self.driver.find_element(by=By.XPATH, value='//*[@id="password"]')
        password_field.send_keys(password)

        audit_submit_button = self.driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div/button')
        audit_submit_button.send_keys(Keys.ENTER)


    def exit_audit_site(self):
        self.driver.quit()
        return "Process: Portico Audit Site checking for book is stopped.\n"

    def search_provider_on_audit_site(self, provider):
        AUDIT_ALL_BOOKS_URL_PROVIDER = f"https://audit.portico.org/Portico/auListView?search={provider}&content=E-Book%2520Content"
        result = None
        global MODE
        self.driver.get(AUDIT_ALL_BOOKS_URL_PROVIDER)
        self.wait.until(ec.visibility_of_element_located((By.ID, "nonMobileContainer")))
        last_height = 0
        if MODE == "LOAD":
            while True:
                self.driver.execute_script('window.scrollBy(0,9000)')
                time.sleep(30)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                print("new_height: ", str(new_height), "last_height: ", str(last_height))

                if new_height == last_height:
                    MODE = "SCRAPE"
                    break
                else:
                    last_height = new_height
                    time.sleep(2)

            global provider_page_source
            provider_page_source = self.driver.page_source
            global source_file_path
            with open(f"{source_file_path}/{provider}_archived_book.html", "w", encoding="utf-8") as source_file:
                source_file.write(provider_page_source)

        else:
            MODE = "SCRAPE"


    def search_isbn_on_audit_site(self, isbn, provider):
        AUDIT_ALL_BOOKS_URL_ISBN = f"https://audit.portico.org/Portico/auListView?search={isbn}&content=E-Book%2520Content"
        result = None
        global MODE

        try:
            self.driver.get(AUDIT_ALL_BOOKS_URL_ISBN)
            self.wait.until(ec.visibility_of_element_located((By.ID, "nonMobileContainer")))
            # nonMobileContainer_element  = self.driver.find_element(By.ID, "nonMobileContainer")
            # self.wait.until(lambda _ : nonMobileContainer_element.is_displayed())

            isbn_page_source = self.driver.page_source
            # print(isbn_page_source)
            global source_file_path
            with open(f"{source_file_path}/{isbn}.html", "w", encoding="utf-8") as isbn_file:
                isbn_file.write(isbn_page_source)

            result = self.find_details_from_source_file(isbn, provider)

            # result = None

        except TimeoutException:
            try:
                self.wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "errorMessage")))
                result = f"ISBN {isbn} not found."
                ISBN_NOT_FOUND_UNDER_CS.append(isbn)
            except TimeoutException:
                result = 501
        except UnicodeEncodeError:
            result = 505
        except MaxRetryError:
            result = 400
        except WebDriverException:
            result = 400


        return result

    def find_details_from_source_file(self, isbn, provider):
        result = ''
        with open(f"{source_file_path}/{isbn}.html", "r", encoding="utf-8") as source_data:
            content = source_data.read()
        # with open(f"{source_file_path}/{provider}_archived_book.html", "r", encoding="utf-8") as source_file_data:
        #     content = source_file_data.read()

        soup = BeautifulSoup(content, "html.parser")
        container_element = soup.find(name="div", id="nonMobileContainer")



        if container_element.find(name="span", class_="cs", text=re.compile(fr'Portico Content Set: {provider}', re.IGNORECASE)):
            table_title = container_element.find(name="span", class_="cs", text=re.compile(fr'Portico Content Set: {provider}', re.IGNORECASE)).parent.parent
            title = table_title.find(name="span", class_="autitle").text
            isbn = table_title.find(name="span", class_="isbn").text
            content_set = table_title.find(name="span", class_="cs").text
            result = f"Book Title: {title} \n {content_set} \n {isbn}\n"
            ISBN_FOUND_UNDER_CS.append(isbn)
            print(f"Book Title: {title} \n {content_set} \n {isbn}\n")
        else:
            all_isbn_elements = container_element.find_all(name="span", class_="isbn")
            ISBN_FOUND_UNDER_OTHER_PROVIDER.append(isbn)
            for isbn in all_isbn_elements:
                content_set = isbn.next_sibling.text
                result += f"{isbn.text} found under the CS {content_set}\n"
                print(f"{isbn.text} found under the CS {content_set}\n")


        return result

def return_found_isbn_under_cs():
        return ISBN_FOUND_UNDER_CS

def return_not_found_in_Audit_site():
    return ISBN_NOT_FOUND_UNDER_CS

def return_isbn_found_under_other_provider():
    return ISBN_FOUND_UNDER_OTHER_PROVIDER


