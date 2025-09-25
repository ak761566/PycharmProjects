from json import JSONDecodeError
from tkinter import *
from tkinter import messagebox

import data_handling
from data_handling import *
from log_handling import *
from portico_audit_check_bot import *
import sys
import os
import json

FONT_NAME = "Courier"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
JOURNAL_TITLE = None
VOLUME = None
ISSUE = None
provider = None

# if getattr(sys, 'frozen', False):
#     base_path = sys._MEIPASS
# else:
#     base_path = os.path.dirname(os.path.abspath(__file__))
#
# log_folder_path = os.path.join(base_path, 'log')
#
# os.makedirs(log_folder_path, exist_ok=True)


class AUDIT_BOT_UI:
    def __init__(self):
        self.audit_window = Tk()
        self.file_path = ''
        #self.login_attempt = login_attempt()
        self.audit_window.minsize(width=600, height=300)
        self.audit_window.title("Portico Audit check bot")
        self.audit_window.config(padx=10, pady=10)
        self.audit_window.resizable(False, False)

        # --------------Frame 1 -----------------------
        self.frame_login = Frame(self.audit_window)
        #self.frame_login.grid(row=0, column=0, pady=20)
        self.frame_login.pack(padx=10, pady=10)

        self.user_name_label = Label(self.frame_login, text="User Name: ", font=(FONT_NAME, 10, "bold"))
        self.user_name_label.grid(row=0, column=0, padx=10)

        self.user_name_entry = Entry(self.frame_login, width=32)
        self.user_name_entry.grid(row=0, column=1, padx=10)

        self.password_label = Label(self.frame_login, text="Password: ", font=(FONT_NAME, 10, "bold"))
        self.password_label.grid(row=0, column=2, padx=10)

        self.password_entry = Entry(self.frame_login, width=32, show="*")
        self.password_entry.grid(row=0, column=3, padx=10)

        # ---------------- Frame 2 ---------------------
        self.choice_frame = Frame(self.audit_window)
        #self.choice_frame.grid(row=1, column=0, pady=5)
        self.choice_frame.pack(padx=10, pady=10)

        self.choice_var = IntVar()

        self.Journal_choice = Radiobutton(self.choice_frame, text="Journal", variable=self.choice_var, value=0)
        self.Journal_choice.grid(row=0, column=0, padx=5)

        self.Book_choice = Radiobutton(self.choice_frame, text="Book", variable=self.choice_var, value=2)
        self.Book_choice.grid(row=0, column=1, padx=5)

        self.Standard_choice = Radiobutton(self.choice_frame, text="Standard", variable=self.choice_var, value=3)
        self.Standard_choice.grid(row=0, column=2, padx=5)


        # --------------Frame 3 -----------------------
        self.audit_frame = Frame(self.audit_window)
        #self.audit_frame.grid(row=2, column=0, pady=5)
        self.audit_frame.pack(padx=10, pady=10)

        self.file_chooser_button = Button(self.audit_frame, text="Select File", font=(FONT_NAME, 10, "bold"), command=self.choose_file)
        self.file_chooser_button.grid(row=0, column=0, pady=20, sticky="w")

        self.sheet_name_label = Label(self.audit_frame, text="Sheet Name", font=(FONT_NAME, 10, "bold"),)
        self.sheet_name_label.grid(row=0, column=1, pady=10)

        self.sheet_name_entry = Entry(self.audit_frame, width=20)
        self.sheet_name_entry.grid(row=0, column=2, pady=10)

        self.provider_name_label = Label(self.audit_frame, text="Provider", font=(FONT_NAME, 10, "bold"), )
        self.provider_name_label.grid(row=0, column=3, pady=10)

        self.provider_name_entry = Entry(self.audit_frame, width=20)
        self.provider_name_entry.grid(row=0, column=4, pady=10)

        self.run_button = Button(self.audit_frame, text="Run", font=(FONT_NAME, 10, "bold"), padx=20, command=self.login)
        self.run_button.grid(row=0, column=5,  padx=5, pady=10)

        self.reset_button = Button(self.audit_frame, text="Reset", font=(FONT_NAME, 10, "bold"), padx=20)
        self.reset_button.grid(row=0, column=6, padx=5, pady=10)



        # --------------Frame 4 -----------------------
        self.result_frame = Frame(self.audit_window)
        #self.result_frame.grid(row=3, column=0, pady=5)
        self.result_frame.pack(padx=10, pady=10)

        self.status_canvas = Canvas(self.result_frame, height=50, width=600)
        self.status_canvas.grid(row=0, column=0, padx=5, sticky="w")
        self.status_canvas_text = self.status_canvas.create_text(300, 25, text="Audit Completeness check bot.",
                                                                 font=(FONT_NAME, 10, "bold"))

        self.result_text = Text(self.result_frame, height=18, width=90)
        self.result_text.insert("1.0", "Required columns in input file are JOURNAL_TITLE	VOLUME	ISSUE and	PROVIDER.\nColumns name should be in all caps and above pattern.")
        self.result_text.grid(row=1, column=0, columnspan=4)


        self.load_data()

        self.audit_window.mainloop()


    def set_file_path(self, path):
        self.file_path = path

    def get_file_path(self):
        return self.file_path
        # try:
        #     with open(os.path.join(log_folder_path, "input_file_details.json"), "r") as input_file_data:
        #         file_details = json.load(input_file_data)
        #         if self.file_path:
        #             return self.file_path
        #         else:
        #             self.file_path = file_details["input_file_name"]
        #             return self.file_path
        # except FileNotFoundError:
        #     pass

    def choose_file(self):
        window_file_path = askopenfilename()
        self.set_file_path(window_file_path)

        input_details = {
            "input_file_name": self.get_file_path(),
        }
        with open(os.path.join(log_folder_path, "input_file_details.json"), "w+") as input_file_data:
            json.dump(input_details, input_file_data, indent=4)

        self.status_canvas.itemconfig(self.status_canvas_text, text=window_file_path)
        self.audit_window.update()


    def login(self):
        if self.user_name_entry.get() == '':
            messagebox.showinfo("User Name:", "Please enter User Name.")
        elif self.password_entry.get() == '':
            messagebox.showinfo("Password:", "Please enter your password.")
        elif self.file_path == '':
            messagebox.showinfo("Input File", "Please select input file.")
        elif self.sheet_name_entry.get() == '':
            messagebox.showinfo("Sheet Name", "Please enter the sheet name.")
        elif self.provider_name_entry.get() == '':
            messagebox.showinfo("Provider Name", "Please enter the provider name.")

        else:

            with open(os.path.join(log_folder_path, "login_data.json"), "w") as login_data:
                data = {
                    "user_name": self.user_name_entry.get(),
                    "password": self.password_entry.get()
                }
                json.dump(data, login_data, indent=4)

            try:
                data_handling.login_in_portico_audit_site(self.user_name_entry.get(), self.password_entry.get())
            except WebDriverException as e:
                self.result_text.delete("1.0", END)
                self.result_text.insert("1.0", "Disconnect VPN before running this App.")
                # print(e)
                # print("Disconnect VPN before running this App.")
            else:
                if self.sheet_name_entry.get() == '':
                    messagebox.showinfo("Sheet Name", "Please enter the sheet name.")
                elif self.sheet_name_entry.get() == self.get_file_path():
                    messagebox.showinfo("Sheet Name", "Please enter the sheet name.")
                elif self.provider_name_entry.get() == '':
                    messagebox.showinfo("Provider Name", "Please enter the provider name.")
                else:
                    input_details = {
                        "input_file_name" : self.get_file_path(),
                        "sheet_name" : self.sheet_name_entry.get(),
                        "provider_name": self.provider_name_entry.get()
                    }
                    with open(os.path.join(log_folder_path, "input_file_details.json"), "w+") as input_file_data:
                        json.dump(input_details, input_file_data, indent=4)

                    data_handling.PROVIDER = self.provider_name_entry.get()


                    window_file_path = self.get_file_path()
                    unix_file_path = window_file_path.replace("C:\\", '').replace("\\", '/')
                    #print("window_file_path", window_file_path)
                    sheet_name = self.sheet_name_entry.get()
                    ui_canvas = self.status_canvas
                    ui_canvas_text = self.status_canvas_text
                    result_text = self.result_text
                    window = self.audit_window
                    provider = self.provider_name_entry.get()



                    if unix_file_path == '':
                        messagebox.showinfo("Input File", "Please select input file.")
                    else:
                        try:
                            data_handling.start_completeness_check_on_audit_site(unix_file_path, sheet_name, result_text, window, provider)
                        except TimeoutError:
                            self.result_text.delete("1.0", END)
                            self.result_text.insert("1.0", "Time out Error. Please try after some time.")

    def load_data(self):
        try:
            with open(os.path.join(log_folder_path, "login_data.json"), "r") as login_data:
                data = json.load(login_data)
                self.user_name_entry.insert(END, data["user_name"])
                self.password_entry.insert(END, data["password"])


            with open(os.path.join(log_folder_path, "input_file_details.json"), "r") as input_file_data:
                    file_data = json.load(input_file_data)
                    self.set_file_path(file_data["input_file_name"])
                    self.status_canvas.itemconfig(self.status_canvas_text, text=file_data["input_file_name"])
                    self.sheet_name_entry.insert(END, file_data["sheet_name"])
                    self.provider_name_entry.insert(END, file_data["provider_name"])

        except FileNotFoundError:
            pass
        except JSONDecodeError:
            pass




