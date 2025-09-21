import json
from xmlrpc.client import DateTime
import os
import sys
from selenium import webdriver
from selenium.common import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException, \
    WebDriverException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import *
from tkinter import *
from tkinter import messagebox
from urllib3.exceptions import MaxRetryError
from win32ctypes.pywin32.pywintypes import datetime
import re
from datetime import datetime, timedelta



JENKINS_URL = " http://pr2ptgpprd31.ithaka.org:9080/jenkins/login?from=%2Fjenkins%2F"
ESTIMATED_TIME = None
CURRENT_TIME = None
TIME_DURATION = None
FUTURE_TIME = None
LOGGED_IN = False

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))

log_folder_path = os.path.join(base_path, 'log')

os.makedirs(log_folder_path, exist_ok=True)

# def jenkins_module_load_again():
#     chrome_option = webdriver.ChromeOptions()
#     #chrome_option.add_argument('--headless')
#     chrome_option.add_experimental_option("detach", True)
#     driver = webdriver.Chrome(options=chrome_option)
#     wait = WebDriverWait(driver, timeout=10)
#     driver.get(JENKINS_URL)


def login_jenkins(submit_button, user_name_text, user_password_text, radio_var, status_canvas, status_canvas_text, driver, wait):
    if len(user_name_text.get()) == 0:
        # messagebox.showerror("User Name", "User Name is required.")
        status_canvas.itemconfig(status_canvas_text, text="User Name is required.")
    elif len(user_password_text.get()) == 0:
        # messagebox.showerror("Password", "Password is required.")
        status_canvas.itemconfig(status_canvas_text, text="Password is required.")
    elif LOGGED_IN is True:
        execute_jenkins(submit_button, radio_var, status_canvas, status_canvas_text, driver, wait)
    else:
        login_data = {
            "user_name": user_name_text.get(),
            "password": user_password_text.get()
        }
        with open(os.path.join(log_folder_path, "login.json"), "w") as data:
            json.dump(login_data, data, indent=4)
        try:
            wait.until(ec.visibility_of_element_located((By.ID, "jenkins")))
            user_name = driver.find_element(By.ID, value="j_username")
            user_name.send_keys(user_name_text.get())
            user_password = driver.find_element(By.CSS_SELECTOR, value="input[name='j_password']")
            user_password.send_keys(user_password_text.get())
            login_button = driver.find_element(By.ID, value="yui-gen1-button")

            login_button.click()
            sleep(5)
            execute_jenkins(submit_button, radio_var, status_canvas, status_canvas_text, driver, wait)
        except WebDriverException:
            status_canvas.itemconfig(status_canvas_text, text="Check VPN Connection.")



def execute_jenkins(submit_button, radio_var, status_canvas, status_canvas_text, driver, wait):
    global  LOGGED_IN
    submit_button['state'] = DISABLED
    wait.until(ec.visibility_of_element_located((By.ID, "page-body")))
    login_failed = driver.find_element(By.CSS_SELECTOR, "div[id='main-panel'] div a")
    if login_failed.text == "Try again":
        login_failed_message = driver.find_element(By.CSS_SELECTOR, "div[id='main-panel'] div")
        status_canvas.itemconfig(status_canvas_text, text=login_failed_message.text)
        submit_button['state'] = NORMAL
        login_failed.click()

        # driver.quit()
        # jenkins_module_load_again()
        # submit_button['state'] = NORMAL
        # with open(os.path.join(log_folder_path, "login.json"), "r") as data:
        #     login_info = json.load(data)

    else:
        LOGGED_IN = True
        innodata_link = driver.find_element(By.PARTIAL_LINK_TEXT, value="-INNODATA")
        setup_link = driver.find_element(By.PARTIAL_LINK_TEXT, value="-SETUP")
        #print(radio_var.get())
        if radio_var.get() == 1:
            innodata_link.click()
            status_canvas.itemconfig(status_canvas_text, text="Logged in..Innodata Jenkins running")
        elif radio_var.get() == 2:
            setup_link.click()
            status_canvas.itemconfig(status_canvas_text, text="Logged in..Setup Jenkins running")
        else:
            #messagebox.showerror("Choice Error", "Select Innodata or Setup option to proceed.")
            status_canvas.itemconfig(status_canvas_text, text="Select Innodata or Setup option to proceed.")
        try:
            wait.until(ec.visibility_of_element_located((By.ID, "page-body")))
            build_now_link = driver.find_element(by=By.LINK_TEXT, value="Build Now")
        except NoSuchElementException:
            pass
        else:
            try:
                build_now_link.click()
            except ElementClickInterceptedException:
                messages = "Build process already running...wait for sometime."
                status_canvas.itemconfig(status_canvas_text, text=messages)
                sleep(5)
                # update_canvas_text(result_text)
                #print("Build process already running...wait for sometime.")
            else:
                messages = "Build process is running...wait for sometime."
                status_canvas.itemconfig(status_canvas_text, text=messages)



def close_jenkins(submit_button, jenkin_window, status_canvas, status_canvas_text, driver, wait):
    global ESTIMATED_TIME, CURRENT_TIME, FUTURE_TIME, TIME_DURATION, LOGGED_IN

    #
    # print(f"{ESTIMATED_TIME} estimated time")
    # print(f"{CURRENT_TIME} current time")
    # print(f"{FUTURE_TIME} future time")

    if ESTIMATED_TIME is None:
        try:
            progress_bar = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "table[class='progress-bar ']")))
            ESTIMATED_TIME = progress_bar.get_attribute("title")
            CURRENT_TIME = datetime.now()

        except TimeoutException:
            status_canvas.itemconfig(status_canvas_text,
                                     text="TimeoutException: May be jenkins build is complete..please check.")
        except MaxRetryError:
            status_canvas.itemconfig(status_canvas_text,
                                     text="MaxRetryError: May be jenkins build is complete..please check.")
    else:
        minutes = re.search('.* (\\d+) min (\\d+) sec$', ESTIMATED_TIME).group(1)
        sec = re.search('.* (\\d+) min (\\d+) sec$', ESTIMATED_TIME).group(2)
        TIME_DURATION = timedelta(minutes=int(minutes), seconds=int(sec))

        FUTURE_TIME = CURRENT_TIME + TIME_DURATION


        if datetime.now() < FUTURE_TIME:
            time_difference = FUTURE_TIME - datetime.now()
            remaining_min = int(time_difference.total_seconds()//60)
            remaining_sec = int(time_difference.total_seconds() % 60)
            status_canvas.itemconfig(status_canvas_text, text=f"Jenkins is running {remaining_min} minutes and {remaining_sec} seconds is remaining.")
        else:
            status_canvas.itemconfig(status_canvas_text,
                                     text=f"Jenkins build is complete.")

            response = messagebox.askokcancel("Jenkins", "Do you wish to continue?")
            if response:
                submit_button['state'] = NORMAL
            else:
                driver.quit()
                jenkin_window.destroy()




        # if LOGGED_IN is True:
        #     result = messagebox.askokcancel("Run Jenkins", "Do you wish to continue?")
        #     print(result)
        #     if result:
        #         LOGGED_IN = False
        #         submit_button['state'] = NORMAL
        #         driver.quit()
        #         window.quit()
        #     else:
        #         driver.quit()
        #         submit_button['state'] = NORMAL
        #         status_canvas.itemconfig(status_canvas_text,
        #                                  text=f"Press Run Jenkins button to build..")








    # try:
    #     div_build_badge = wait.until(
    #         ec.visibility_of_element_located((By.CSS_SELECTOR, "div[class='middle-align build-badge']")))
    # except TimeoutException:
    #     status_canvas.itemconfig(status_canvas_text, text="TimeoutException: May be jenkins build is complete..please check.")
    # except MaxRetryError:
    #     status_canvas.itemconfig(status_canvas_text, text="MaxRetryError: May be jenkins build is complete..please check.")
    # else:
    #     div_build_badge_style = div_build_badge.get_attribute("style")
    #     if div_build_badge_style == "width: 100%;":
    #         messages = "Build process is complete."
    #         status_canvas.itemconfig(status_canvas_text, text=messages)
    #         driver.quit()
    #         window.quit()
    #     else:
    #         messages = f"Build process is running ({div_build_badge_style.split()[-1].replace('px','%').replace(';','')} is complete)...wait for sometime."
    #         status_canvas.itemconfig(status_canvas_text, text=messages)

