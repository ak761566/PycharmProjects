import json
import os
import sys
from tkinter import *
from tkinter import messagebox
from pyexpat.errors import messages

import jenkins_build
from selenium import webdriver
from selenium.common import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException, \
    WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


FONT_NAME = "Courier"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
USER_NAME = ''
PASSWORD = ''
JENKINS_URL = " http://pr2ptgpprd31.ithaka.org:9080/jenkins/login?from=%2Fjenkins%2F"



class UI:
    def __init__(self, driver, wait, username='', password=''):
        self.jenkin_window = Tk()
        self.status_canvas_text = None
        #self.driver = jenkins.driver
        self.jenkin_window.title("Portico Jenkins")
        self.jenkin_window.minsize(width=600, height=300)
        self.jenkin_window.config(padx=10, pady=10)

        self.frame_1 = Frame(self.jenkin_window)
        self.frame_1.grid(row=0, column=0, padx=10, pady=10)

        self.user_name_label = Label(self.frame_1, text="User Name:", font=(FONT_NAME, 10, "bold"))
        self.user_name_label.grid(row=0, column=0, padx=30, pady=10)

        self.user_name_text = Entry(self.frame_1, width=30)
        self.user_name_text.grid(row=0, column=1, padx=10, pady=10)

        self.user_password_label = Label(self.frame_1, text="Password: ", font=(FONT_NAME, 10, "bold"))
        self.user_password_label.grid(row=1, column=0, padx=30, pady=10)

        self.user_password_text = Entry(self.frame_1, width=30, show="*")
        self.user_password_text.grid(row=1, column=1, padx=10, pady=10)

        self.radio_var = IntVar()

        self.innodata_jenkins = Radiobutton(self.frame_1, text="Innodata Jenkins", variable=self.radio_var, value=100, padx=20,
                                       font=(FONT_NAME, 10, "italic"))
        self.innodata_jenkins.grid(row=2, column=0, padx=20, pady=20)

        self.setup_jenkins = Radiobutton(self.frame_1, text="Setup Jenkins", variable=self.radio_var, value=200, padx=20,
                                    font=(FONT_NAME, 10, "italic"))
        self.setup_jenkins.grid(row=2, column=1, padx=20, pady=20)

        self.radio_var.set(1)

        self.status_canvas = Canvas(self.jenkin_window, height=50, width=600, bg="yellow")
        self.status_canvas.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.status_canvas_text = self.status_canvas.create_text(280, 25, text="Press Run Jenkins button to build.",
                                                                 font=(FONT_NAME, 10, "italic"))

        self.submit_button = Button(self.frame_1, text="Run Jenkins", font=(FONT_NAME, 10, "bold"), command=lambda : jenkins_build.login_jenkins(self.submit_button, self.user_name_text, self.user_password_text, self.radio_var, self.status_canvas, self.status_canvas_text, driver, wait))
        self.submit_button.grid(row=3, column=0, padx=10, pady=10)


        self.close_button = Button(self.frame_1, text="Build Status", padx=20, font=(FONT_NAME, 10, "bold"), command=lambda : jenkins_build.close_jenkins(self.submit_button, self.jenkin_window, self.status_canvas, self.status_canvas_text, driver, wait))
        self.close_button.grid(row=3, column=1, padx=20, pady=10)



        # self.status_canvas = my_canvas(height=50, width=600, x=200, y=25, text="Press Run Jenkins button to build.")
        # self.status_canvas.setup_my_canvas(row=3, col=0)


        self.load_data()

        self.jenkin_window.mainloop()

    def load_data(self):
        global USER_NAME, PASSWORD
        try:
            with open(os.path.join(jenkins_build.log_folder_path, "login.json"), "r") as login_data:
                data = json.load(login_data)
            USER_NAME = data['user_name']
            PASSWORD = data['password']
            # print(USER_NAME, PASSWORD)
            if USER_NAME is not None and PASSWORD is not None:
                self.user_name_text.insert(END, data["user_name"])
                self.user_password_text.insert(END, data["password"])
        except FileNotFoundError:
            pass
            # login_data = {
            #     "user_name": self.user_name_text.get(),
            #     "password" :self.user_password_text.get()
            # }
            # with open("./log/login.json", "w") as login_file:
            #     json.dump(login_data, login_file, indent=4)


def jenkins_module():
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--headless')
    chrome_option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_option)
    wait = WebDriverWait(driver, timeout=10)
    try:
        driver.get(JENKINS_URL)
    except WebDriverException:
        messagebox.showinfo("VPN Connection", "Check VPN connection.")
    else:
        UI(driver, wait, USER_NAME, PASSWORD)


