import re
from time import sleep

from selenium import webdriver
from selenium.common import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
import requests
import os
import sys
import time

found_journal_title_list = []

if getattr(sys, 'Frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))


html_folder_path = os.path.join(base_path, "source_html")

os.makedirs(html_folder_path, exist_ok=True)

PORTICO_AUDIT_SITE_URL = "https://audit.portico.org/Portico/login.html"
SEARCHED_TITLE_LIST = []
class NewAuditCheckAgent:
    def __init__(self, username, password):
        self.chrome_option = webdriver.ChromeOptions()
        #self.chrome_option.add_argument("--headless")
        self.chrome_option.add_experimental_option("detach", True)

        self.driver = webdriver.Chrome(options=self.chrome_option)
        self.wait  = WebDriverWait(self.driver, timeout=10)
        self.driver.get(PORTICO_AUDIT_SITE_URL)
        self.login_portico_audit_site(username,password)


    def login_portico_audit_site(self, username, password):
        audit_site_username = self.driver.find_element(by=By.XPATH, value='//*[@id="username"]')
        audit_site_username.send_keys(username)
        audit_site_password = self.driver.find_element(by=By.XPATH, value='//*[@id="password"]')
        audit_site_password.send_keys(password)
        audit_site_submit = self.driver.find_element(by=By.XPATH, value='//*[@id="loginForm"]/div/button')
        audit_site_submit.send_keys(Keys.ENTER)

    def search_journal_title_on_audit_site(self, journal_title, volume, issue, publication_year ,provider):
        content_set = None
        title_text = None
        journal_title_text = None
        content_set = None

        params = {
            "ACCEPT-LANGUAGE" : "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "USER-AGENT" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }

        if journal_title not in found_journal_title_list:

            search_journals_page_url = f"https://audit.portico.org/Portico/csListView?search={journal_title.replace('&', '%26')}&content=E-Journal%20Content"
            self.driver.get(search_journals_page_url)
            # print("provider.upper(): ",provider.upper())
            try:
                self.wait.until(ec.visibility_of_element_located((By.XPATH, f"//*[@id='nonMobileContainer']//div[10][a[@href='/Portico/pubView?id={provider.upper()}']]")))
                div_table_titles = self.driver.find_elements(By.XPATH, f"//*[@id='nonMobileContainer']/div[div[10][a[@href='/Portico/pubView?id={provider.upper()}']]]")
                # print(f"length of div_table_titles {len(div_table_titles)}")

                for title in div_table_titles:
                    try:
                        journal_title_text = title.find_element(By.XPATH, f"div[1]/a").text
                        # print("journal_title_text", journal_title_text)
                        content_set = title.find_element(By.XPATH, f"div[1]/span").text
                        # print("content_set", content_set)
                        # print(f"https://audit.portico.org/Portico/rest/cmi/getCompletenessReport?cs={content_set}")
                        self.driver.get(f"https://audit.portico.org/Portico/rest/cmi/getCompletenessReport?cs={content_set}")
                        page_source = self.driver.page_source
                        #print(page_source)
                        with open(f"{html_folder_path}/{journal_title}.html", "w") as html_file:
                            html_file.write(page_source)

                        found_journal_title_list.append(journal_title)
                        #print(found_journal_title_list)
                        result = self.find_completness_report(journal_title, volume, issue, publication_year)
                        print(result)
                        return result
                    except StaleElementReferenceException:
                        pass
                    except TimeoutException:
                        pass
            except TimeoutException:
                ## Case where Journal title not found on Audit Site
                return 501
        else:
            #print(found_journal_title_list)
            result = self.find_completness_report(journal_title, volume, issue, publication_year)
            #response = f"{journal_title_text} \n {content_set} \n Issue completeness report:\n {result} "
            print(result)
            return result


    def find_completness_report(self, journal_title, volume, issue, publication_year):
        with open(f"{html_folder_path}/{journal_title}.html", "r") as html_file:
            content = html_file.read()
            soup = BeautifulSoup(content, "html.parser")
            table_element = soup.find(name="table")
            #print(soup.table)
            print(f"volume {volume}")
            print(f"issue {issue}")
            print(f"publication year {publication_year}")

            if volume == 'nan' or volume == '':
                volume_search_pattern = fr".*\({publication_year}.*"
            else:
                if re.match(r'\d\d\d\d', volume):
                    volume_search_pattern = fr".*\({volume}.*"
                else:
                    volume_search_pattern = fr"v.{volume}.*"

            print("volume_search_pattern: ", volume_search_pattern)
            target_td  = table_element.find(text=re.compile(volume_search_pattern)).parent
            print(target_td)
            target_row =  target_td.parent
            print("target_row\n", target_row)
            if re.match(r'\d\.\d',issue):
                print("m1")
                custom_issue = re.match(r'\d\.(\d)', issue).group(1)
                issue_search_pattern = fr"n.{custom_issue}"
            elif re.match(r'\d+\s*\(\d\d\d\d\)\s*\d+', issue):
                print("m2")
                custom_issue = re.match(r'\d+\s*\(\d\d\d\d\)\s*(\d+)', issue).group(1)
                issue_search_pattern = fr"n.{custom_issue}"
            else:
                print("m3")
                issue_search_pattern = fr"n.{issue}"

            print("issue_search_pattern: ", issue_search_pattern )
            target_li  = target_row.find(text=re.compile(issue_search_pattern))
            print("target_li: ", target_li)
            target_ul = target_li.parent.parent
            print("target_td:", target_td)
            print("target_ul: ", target_ul)
            return f"Journal Title : {journal_title} \n Volume: {volume} \n Issue: {issue} \n Issue Completeness Report:  {target_td.text} {target_ul.text}"



