from itertools import dropwhile
from pickle import GLOBAL
from tkinter import *
from time import sleep
from tkinter.filedialog import askopenfilename

from openpyxl.styles.builtins import title
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, NoSuchWindowException, \
    StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from urllib3.exceptions import MaxRetryError

import audit_bot_ui as ui
import re

AUDIT_URL = "https://audit.portico.org/Portico/login.html"
RESPONSE = None

months = {
    "1" : "January",
    "2" : "February",
    "3" : "March",
    "4" : "April",
    "5" : "May",
    "6" : "June",
    "7" : "July",
    "8" : "August",
    "9" : "September",
    "10" : "October",
    "11" : "November",
    "12" : "December"
}


class PorticoAuditCheckerBot:
    def __init__(self, user_name, password):
        self.chrome_option = webdriver.ChromeOptions()
        self.chrome_option.add_argument('--headless')
        self.chrome_option.add_experimental_option('detach', True)

        self.driver = webdriver.Chrome(options=self.chrome_option)
        self.wait = WebDriverWait(self.driver, timeout=10)
        self.driver.get(AUDIT_URL)
        try:
            self.wait.until(ec.visibility_of_element_located((By.NAME, 'submit')))
            self.username_field = self.driver.find_element(By.ID, 'username')
            self.username_field.send_keys(user_name)
            self.password_field = self.driver.find_element(By.ID, "password")
            self.password_field.send_keys(password)
            self.submit_button = self.driver.find_element(By.NAME, 'submit')
            self.submit_button.send_keys(Keys.ENTER)
            #self.submit_button.click()

        except NoSuchWindowException:
            pass

        self.volume_driver = None
        # driver.quit()

    def check_journal_title_on_audit(self, quit_driver, journal_title, volume, issue, publication_year, provider):
        global RESPONSE
        URL = f"https://audit.portico.org/Portico/csListView?search={journal_title.replace('&', '%26')}&content=E-Journal%20Content"

        try:
            print("debug-1")
            self.driver.get(URL)
            self.wait.until(ec.visibility_of_element_located((By.ID, "nonMobileContainer")))
            table_titles = self.driver.find_elements(By.XPATH, f"//app-cslist-data/div[@id='nonMobileContainer']/div[div[a[contains(@href, '/Portico/pubView?id={provider.upper()}')]]]")
            print("def check_journal_title_on_audit", [title.text for title in table_titles])
        except NoSuchElementException:
            print("debug-2")
            #print(f"Journal title '{journal_title}' under the provider '{provider}' is not available. Please check.")
            return 502
        except TimeoutException:
            print("debug-3")
            # errorMessage = self.driver.find_element(By.CLASS_NAME, "errorMessage")
            #print(errorMessage.text)
            return 501
        else:
            print("debug-4")
            #print(table_title.get_attribute("outerHTML"))
            #ec.visibility_of_element_located((By.XPATH, "div[@class='table-title wrapText w-25']/span"))

            if len(table_titles) == 0:
                RESPONSE = 502

            try:
                length_of_table_titles = len(table_titles)

                print(f"journal-title {journal_title} and length_of_table_titles", length_of_table_titles)
                counter = 1
                for title in table_titles:
                    counter +=1
                    # print(f"counter {counter} title {title.text}")
                    if title.find_element(By.XPATH, "div[@class='table-title wrapText w-25']/a").text.lstrip().rstrip() == journal_title:
                        #print("d1", title.text)
                        content_set = title.find_element(By.XPATH, "div[@class='table-title wrapText w-25']/span")
                        content_set_name = content_set.text
                        RESPONSE = self.check_content_set_on_audit(content_set_name, volume, issue, publication_year)

                    # If journal title is not exactly matching on Audit site than look for partial match.
                    elif journal_title in title.find_element(By.XPATH, "div[@class='table-title wrapText w-25']/a").text and counter == length_of_table_titles:
                        #print("d2", title.text)
                        content_set = title.find_element(By.XPATH, "div[@class='table-title wrapText w-25']/span")
                        content_set_name = content_set.text
                        RESPONSE = self.check_content_set_on_audit(content_set_name, volume, issue, publication_year)
                    else:
                        RESPONSE = 502
            except StaleElementReferenceException:
                #print("def check_journal_title_on_audit - debugging-1")
                pass

            return RESPONSE

        finally:
            if quit_driver:
                self.driver.quit()
            #return RESPONSE

    def force_quit_driver(self):
        self.driver.quit()

    def check_content_set_on_audit(self, content_set_name, volume, issue, publication_year):
        #print(f"check_content_set_on_audit: CS : {content_set_name}, volume : {volume}, issue {issue}, publication_year: {publication_year}")
        try:
            self.driver.get(f"https://audit.portico.org/Portico/rest/cmi/getCompletenessReport?cs={content_set_name}")

        except NoSuchElementException:
            error_message = self.driver.find_element(By.CSS_SELECTOR, "div div div")
            return error_message.text
        else:

            title = self.driver.find_element(By.CLASS_NAME, "p-title")
            content_set_id = self.driver.find_element(By.XPATH, '//div[starts-with(., "Content Set ID")]')
            completeness_table = self.driver.find_element(By.CLASS_NAME, "completeness")
            sleep(2)

            try:
                ## search issue based on the given volume

                if volume == "nan" or volume == '':
                    # print('volume == "nan"')
                    target_volume_row = completeness_table.find_elements(By.XPATH,
                                                                    f"//tr[self::*[1][td[not(*) and contains(., '{publication_year}')]]]")
                elif volume == "0":
                    # print('volume == "0"')
                    target_volume_row = completeness_table.find_elements(By.XPATH,

                                                                       f"//tr[self::*[1][td[not(*) and contains(., '{publication_year}')]]]")
                elif re.match('\\d\\d\\d\\d',volume):
                    target_volume_row = completeness_table.find_elements(By.XPATH,
                                                                         f"//tr[td[not(*) and contains(., '{volume}')]]")
                else:
                    target_volume_row = completeness_table.find_elements(By.XPATH,
                                                                             f"//tr[td[not(*) and contains(., 'v.{volume}')]]")

                # debug_text = [item.text + "\n\n" for item in target_volume_row]
                # print("debug_text-1", debug_text)

                # self.volume_driver = target_volume
                # print("target_volume_row: ", target_volume_row.text)
                RESPONSE = self.check_issue_on_audit_site(target_volume_row=target_volume_row, issue=issue, title=title, content_set_id=content_set_id)

                # RESPONSE = self.check_issue_status(audit_window, result_text, volume, issue, title, content_set_id)
                return RESPONSE
            except NoSuchElementException:
                try:
                    ## search issue based on the given publication year

                    # print("check_content_set_on_audit-2")
                    target_volume_row = completeness_table.find_elements(By.XPATH, f"//tr[self::*[1][td[not(*) and contains(., '{publication_year}')]]]")
                except NoSuchElementException:
                    if publication_year is not None:
                        RESPONSE = title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + publication_year + "\n\n" + f"Volume/Year {volume} Issue {issue} is missing on the Portico Audit site."
                    else:
                        RESPONSE = title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + "\n\n" + f"Volume/Year {volume} Issue {issue} is missing on the Portico Audit site."
                    return RESPONSE
                else:
                    # self.volume_driver = target_volume
                    RESPONSE = self.check_issue_on_audit_site(target_volume_row=target_volume_row, issue=issue, title=title, content_set_id=content_set_id)
                    return RESPONSE

    def check_issue_on_audit_site(self, target_volume_row, issue, title, content_set_id):
        # print(f"check_issn_on_audit_site:  volume : {volume}, issue {issue}, title: {title.text}, CS : {content_set_id.text}")
        #print(target_volume_row.text)

        if re.match("\\d+\\.\\d+",issue):
            issue = re.search("\\d+\\.(\\d+)", issue).group(1)

        # print("debug_text-issue", issue)
        # debug_text = [item.text + "\n\n" for item in target_volume_row]
        # print("debug_text-1", debug_text)

        try:
            # Search issue pattern ex n.9 or n.12

            result_text = ''
            for issue_item in target_volume_row:
                issue_name = issue_item.find_element(By.XPATH, 'td[1]')
                issue_details = issue_item.find_element(By.XPATH, f"td[ul[starts-with(li, 'n.{issue}')]]")
                result_text += title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + issue_name.text + "\n" + issue_details.text + "\n\n"

            return result_text
        except NoSuchElementException:
            response_text = ''
            issue_name = None
            try:
                # Search issue pattern ex n.March or n.April

                for issue_item in target_volume_row:
                    issue_name = issue_item.find_element(By.XPATH, 'td[1]')
                    issue_details = issue_item.find_element(By.XPATH, f"td[ul[starts-with(li, 'n.{months[issue]}')]]")
                    response_text += title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + issue_name.text + "\n" + issue_details.text + "\n\n"

                return response_text
            except NoSuchElementException:
                # If all search for the issue fail then grab all the issue listed under the identified volume.

                none_target_issue= []
                for issue_item in target_volume_row:
                    issue_name = issue_item.find_element(By.XPATH, 'td[1]')
                    td_list = issue_item.find_elements(By.TAG_NAME, "td")
                    target_list = [td.text + "\n" for td in td_list]
                    none_target_issue.append(target_list)

                for item_list in none_target_issue:
                    for item in item_list:
                        response_text += item
                        response_text += "\n"

            except KeyError:
                # If all search for the issue fail then grab all the issue listed under the identified volume.
                none_target_issue= []
                # debug_text = [item.text + "\n\n" for item in target_volume_row]
                # print("debug_text-2", debug_text)

                for issue_item in target_volume_row:
                    # debug_text = issue_item.text
                    # print(debug_text)
                    issue_name = issue_item.find_element(By.XPATH, 'td[1]')
                    td_list = issue_item.find_elements(By.TAG_NAME, "td")
                    target_list = [td.text + "\n" for td in td_list]
                    none_target_issue.append(target_list)
                    # print("debug-3:", target_issue)

                for item_list in none_target_issue:
                    for item in item_list:
                        response_text += item
                        response_text += "\n"

            return title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + issue_name.text  + "\n\n" + response_text






















































#----------------------------- Old Code ------------------------------------------------------------- #

# ----------------------------- Old Code ------------------------------------------------------------- #

    def issue_completeness_report_journal_title(self, audit_window, result_text, url=None, journal_title=None, volume=None, issue=None, pub_date=None, provider=None):
        URL = f"https://audit.portico.org/Portico/csListView?search={journal_title.replace('&','%26')}&content=E-Journal%20Content"
        self.driver.get(URL)

        result_text.delete("1.0", END)
        result_text.insert("1.0", "Searchin Journal Title....")
        audit_window.update()
        try:

            self.wait.until(ec.visibility_of_element_located((By.ID, "nonMobileContainer")))
            table_titles = self.driver.find_element(By.XPATH, f"//div[@id='nonMobileContainer']")
            table_title = table_titles.find_element(By.XPATH, f"div[div[a[contains(@href, '/Portico/pubView?id={provider.upper()}')]]]")
        except NoSuchElementException:

            # print(f"Journal title '{journal_title}' under the provider '{provider}' is not available. Please check.")
            return f"Journal title '{journal_title.lstrip().rstrip()}' under the provider '{provider}' is not available. Please check."
        except TimeoutException:
            errorMessage = self.driver.find_element(By.CLASS_NAME, "errorMessage")
            return errorMessage.text
        except TimeoutError:
            print("Could not reach to the server. Timeout Error")
        else:
            #print(table_title.get_attribute("outerHTML"))
            content_set = table_title.find_element(By.XPATH, "div[@class='table-title wrapText w-25']/span")
            #print(content_set.text)

            result_text.delete("1.0", END)
            result_text.insert("1.0", "Searching content set....")
            audit_window.update()
            response = self.issue_completeness_report_issn(audit_window, result_text, URL, content_set_name=content_set.text, volume=volume, issue=issue, provider=provider)
            return response
        finally:
            self.driver.quit()


    def issue_completeness_report_issn(self, audit_window, result_text,  url=None, content_set_name=None, volume=None, issue=None, provider=None):
        global RESPONSE
        try:
            self.driver.get(f"https://audit.portico.org/Portico/rest/cmi/getCompletenessReport?cs={content_set_name}")

        except NoSuchElementException:
            error_message = self.driver.find_element(By.CSS_SELECTOR, "div div div")
            return error_message.text
        else:
            result_text.delete("1.0", END)
            result_text.insert("1.0", f"Searching volume and issue for the content set {content_set_name}....")
            audit_window.update()

            title = self.driver.find_element(By.CLASS_NAME, "p-title")
            content_set_id = self.driver.find_element(By.XPATH, '//div[starts-with(., "Content Set ID")]')

            completeness_table = self.driver.find_element(By.CLASS_NAME, "completeness")
            sleep(2)
            try:
                target_volume = completeness_table.find_element(By.XPATH, f"//tr[starts-with(td,'v.{volume}')]")
                self.volume_driver = target_volume

                RESPONSE = self.check_issue_status(audit_window, result_text, volume, issue, title, content_set_id)
            except NoSuchElementException:
                try:
                    target_volume = completeness_table.find_element(By.XPATH, f"//tr[contains(td,'{volume}')]")
                except NoSuchElementException:
                    RESPONSE = title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + volume + "\n\n" + f"Volume/Year {volume} Issue {issue} is missing on the Portico Audit site."
                else:
                    self.volume_driver = target_volume
                    RESPONSE = self.check_issue_status(audit_window, result_text, volume, issue, title, content_set_id)

            return RESPONSE


    def check_issue_status(self, audit_window, result_text,  volume, issue, title, content_set_id):
        try:
            target_issue = self.volume_driver.find_element(By.XPATH, f"td[ul[starts-with(li, 'n.{issue}')]]")
            return title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " +  volume + "\n\n" + target_issue.text

        except NoSuchElementException:
            td_list = self.volume_driver.find_elements(By.TAG_NAME, "td")
            target_issue = [td.text + "\n" for td in td_list]
            response_text = ''
            for item in target_issue:
                response_text += item
                response_text += "\n"

            return title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " +  volume + "\n\n" + response_text

