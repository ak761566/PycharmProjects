from itertools import dropwhile
from pickle import GLOBAL
from tkinter import *
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, NoSuchWindowException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

AUDIT_URL = "https://audit.portico.org/Portico/login.html"
RESPONSE = None
LOGIN_RESULT = False

def create_web_driver():
    chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument('--headless')
    chrome_option.add_experimental_option('detach', True)
    driver = webdriver.Chrome(options=chrome_option)
    driver.get(AUDIT_URL)
    return driver


def create_wait_driver(driver):
    wait = WebDriverWait(driver, timeout=10)
    return wait

def login_audit_site(driver,status_canvas, status_canvas_text, result_text, username, password):
    global LOGIN_RESULT
    #print(result_text.get("1.0", "end-1c"))
    # status_canvas.itemconfig(status_canvas_text, text="Logging in...")
    #print("Logging in...")
    try:
        username_field = driver.find_element(By.ID, 'username')
        username_field.send_keys(username)
        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(password)
        submit_button = driver.find_element(By.NAME, 'submit')
        submit_button.click()
        LOGIN_RESULT = True
        print("Logged in..")
    except NoSuchWindowException:
        pass
    return LOGIN_RESULT

def issue_completeness_report_journal_title(driver, wait, journal_title=None, volume=None, issue=None, provider=None):
    URL = f"https://audit.portico.org/Portico/csListView?search={journal_title.replace('&', '%26')}&content=E-Journal%20Content"
    driver.get(URL)
    #sleep(5)
    print("Checking journal title on Audit Site")
    try:

        wait.until(ec.visibility_of_element_located((By.ID, "nonMobileContainer")))
        table_titles = driver.find_element(By.XPATH, f"//div[@id='nonMobileContainer']")
        #sleep(2)
        table_title = table_titles.find_element(By.XPATH,
                                                f"div[div[a[contains(@href, '/Portico/pubView?id={provider.upper()}')]]]")
    except NoSuchElementException:

        return f"Journal title '{journal_title.lstrip().rstrip()}' under the provider '{provider}' is not available. Please check."
    except TimeoutException:
        errorMessage = driver.find_element(By.CLASS_NAME, "errorMessage")
        return errorMessage.text
    else:
        print("Checking volume and issue on Audit Site")
        content_set = table_title.find_element(By.XPATH, "div[@class='table-title wrapText w-25']/span")
        response = issue_completeness_report_issn(driver, URL, content_set_name=content_set.text, volume=volume,
                                                       issue=issue, provider=provider)
        return response
    finally:
        #print("driver ended by issue_completeness_report_journal_title()")
        driver.quit()


def issue_completeness_report_issn(driver, url=None, content_set_name=None, volume=None, issue=None, provider=None):
    global RESPONSE
    try:
        driver.get(f"https://audit.portico.org/Portico/rest/cmi/getCompletenessReport?cs={content_set_name}")
    except NoSuchElementException:
        error_message = driver.find_element(By.CSS_SELECTOR, "div div div")
        return error_message.text
    else:
        print("Checking volume..")
        title = driver.find_element(By.CLASS_NAME, "p-title")
        content_set_id = driver.find_element(By.XPATH, '//div[starts-with(., "Content Set ID")]')
        completeness_table = driver.find_element(By.CLASS_NAME, "completeness")
        #sleep(2)
        try:

            target_volume = completeness_table.find_element(By.XPATH, f"//tr[starts-with(td,'v.{volume}')]")
            volume_driver = target_volume
            print("Found volume, checking issue..")
            RESPONSE = check_issue_status(volume_driver, volume, issue, title, content_set_id)
        except NoSuchElementException:
            try:
                target_volume = completeness_table.find_element(By.XPATH, f"//tr[contains(td,'{volume}')]")
            except NoSuchElementException:
                RESPONSE = title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + volume + "\n\n" + f"Volume/Year {volume} Issue {issue} is missing on the Portico Audit site."
            else:
                volume_driver = target_volume
                RESPONSE = check_issue_status(volume_driver, volume, issue, title, content_set_id)

        return RESPONSE
    # finally:
    #     print("driver ended by issue_completeness_report_issn()")
    #     driver.quit()


def check_issue_status(volume_driver, volume, issue, title, content_set_id):
    try:
        print("Checking issue..")
        target_issue = volume_driver.find_element(By.XPATH, f"td[ul[starts-with(li, 'n.{issue}')]]")
        print("Found issue..preparing report.")
        return title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + volume + "\n\n" + target_issue.text

    except NoSuchElementException:
        td_list = volume_driver.find_elements(By.TAG_NAME, "td")
        target_issue = [td.text + "\n" for td in td_list]
        response_text = ''
        for item in target_issue:
            response_text += item
            response_text += "\n"
        print("Not Found issue..preparing report.")
        return title.text + "\n" + content_set_id.text + "\n" + "Volume/Year: " + volume + "\n\n" + response_text
