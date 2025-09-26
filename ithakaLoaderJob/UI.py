from gc import collect

import requests
from tkinter import *
from tkinter import messagebox
from loader_functions import LoaderFunction

import json

FONT_NAME = "Courier"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"


class WorkbenchInterface:


    def __init__(self):
        # self.end_points = self.return_endpoint()
        self.loader_function = LoaderFunction()
        self.window = Tk()
        self.window.title("Ithaka Loader - Workbench")
        self.window.config(padx=50, pady=50)

        self.radio_state = IntVar()

        self.setup_WB_radio_button = Radiobutton(text="Setup Workbench Loader", variable=self.radio_state, value=1)
        # self.setup_WB_radio_button.focus()
        self.setup_WB_radio_button.grid(row=0, column=0)
        self.setup_WB_radio_button.config(pady=20, padx=20)

        self.innodata_WB_radio_button = Radiobutton(text="Innodata Workbench Loader", variable=self.radio_state, value=2)
        self.innodata_WB_radio_button.grid(row=0, column=1)
        self.innodata_WB_radio_button.config(pady=20, padx=20)

        self.ingest_WB_radio_button = Radiobutton(text="Ingest Workbench Loader", variable=self.radio_state, value=3)
        self.ingest_WB_radio_button.grid(row=0, column=2)
        self.ingest_WB_radio_button.config(pady=20, padx=20)

        # Use the set() method on the shared Tkinter variable to specify the initial selected value.
        self.radio_state.set(1)

        self.propertyFileName_label = Label(text="Property File Name: ")
        self.propertyFileName_label.grid(row=1, column=0)
        self.propertyFileName_label.config(padx=10, pady=10)

        self.loaderProfileFileName_label = Label(text="Loader Profile Name: ")
        self.loaderProfileFileName_label.grid(row=2, column=0)
        self.loaderProfileFileName_label.config(padx=10, pady=10)

        self.propertyFileName_entry = Entry(width=50)
        self.propertyFileName_entry.grid(row=1, column=1, columnspan=2)

        self.loaderProfileFileName_entry = Entry(width=50)
        self.loaderProfileFileName_entry.grid(row=2, column=1, columnspan=2)

        self.run_loader_button = Button(text="Execute Loader", highlightthickness=0, command=self.execute_loader)
        self.run_loader_button.grid(row=3, column=1)

        self.canvas = Canvas(height=100, width=300)
        self.canvas.grid(row=4, column=0, columnspan=3)
        self.canvas_text = self.canvas.create_text(150, 50, text="Loader - Workbench", font=(FONT_NAME, 10, "italic"))

        self.check_status_button = Button(text="Check Job Status", highlightthickness=0, command=self.check_job_status)
        self.check_status_button.grid(row=5, column=1)

        self.check_job_status()
        self.window.mainloop()


    def return_endpoint(self):
        loader_endpoint = ''
        status_endpoint = ''
        # print(self.radio_state.get())
        if self.radio_state.get() == 1:
            loader_endpoint = "http://pr2ptgpprd43.ithaka.org:9500/loader/job/multistepjob/v1/submitwithjsonandparams/LoaderJob"
            status_endpoint = "http://pr2ptgpprd43.ithaka.org:9500/loader/job/v1/status/"

            self.loader_function.set_loader_end_point(loader_endpoint)
            self.loader_function.set_status_endpoint(status_endpoint)
        elif self.radio_state.get() == 2:
            loader_endpoint = "http://pr2ptgpprd42.ithaka.org:9500/loader/job/multistepjob/v1/submitwithjson/LoaderJob"
            status_endpoint = "http://pr2ptgpprd42.ithaka.org:9500/loader/job/v1/status/"

            self.loader_function.set_loader_end_point(loader_endpoint)
            self.loader_function.set_status_endpoint(status_endpoint)

        elif self.radio_state.get()  == 3:
            loader_endpoint = "http://pr2ptgpprd02.ithaka.org:9500/loader/job/multistepjob/v1/submitwithjsonandparams/LoaderJob"
            status_endpoint = "http://pr2ptgpprd02.ithaka.org:9500/loader/job/v1/status/"

            self.loader_function.set_loader_end_point(loader_endpoint)
            self.loader_function.set_status_endpoint(status_endpoint)



    def execute_loader(self):

        self.return_endpoint()
        property_file_name = self.propertyFileName_entry.get()
        loader_profile_name = self.loaderProfileFileName_entry.get()

        if len(property_file_name) == 0:
            messagebox.showinfo("Property File", "Please enter property file name.")
        if len(loader_profile_name) == 0:
            messagebox.showinfo("Loader Profile", "Please enter loader profile name.")
        else:
            json_data = self.loader_function.save_json_data(property_file_name, loader_profile_name)
            is_loader_ran = self.loader_function.run_loader(json_data)
            if is_loader_ran:
                with open("job_id.json", "r") as json_file:
                    content = json.load(json_file)

                with open("loader_config.json", "r") as confg_file:
                    config_data = json.load(confg_file)

                self.canvas.itemconfig(self.canvas_text, text=f"Job Status: {content["jobStatus"]}\n Job Id: {content["jobId"]}")
                self.run_loader_button.config(state="disabled")
                self.check_status_button.config(state="normal")

                if len(self.propertyFileName_entry.get()) == 0:
                    self.propertyFileName_entry.insert(0, config_data["propertyFileName"])

                if len(self.loaderProfileFileName_entry.get()) == 0:
                    self.loaderProfileFileName_entry.insert(0, config_data["loaderProfileFileName"])



    def check_job_status(self):
        try:
            with open("job_id.json", "r") as job_id_file:
                data = json.load(job_id_file)

            with open("loader_config.json", "r") as config_file:
                config_data = json.load(config_file)
        except FileNotFoundError:
            self.check_status_button.config(state="disabled")
            self.canvas.itemconfig(self.canvas_text,
                                   text=f"Run Loader")
        else:
            if len(self.propertyFileName_entry.get()) == 0:
                self.propertyFileName_entry.insert(0, config_data["propertyFileName"])
            if len(self.loaderProfileFileName_entry.get()) == 0:
                self.loaderProfileFileName_entry.insert(0, config_data["loaderProfileFileName"])

            response = self.loader_function.check_job_status(data["jobId"])

            try:
                response.raise_for_status()
            except Exception:
                if response.json()["jobResult"] == "EXECUTING":
                    self.run_loader_button.config(state="disabled")
                else:
                    self.run_loader_button.config(state="normal")

                self.canvas.itemconfig(self.canvas_text,
                                       text=f"Server Response Code: {response.status_code}"
                                            f"\n Job Id: {response.json()["jobId"]}"
                                            f"\n Job Status: {response.json()["jobStatus"]}"
                                            f"\n Job Result: {response.json()["jobResult"]}")
            else:
                if response.json()["jobResult"] == "EXECUTING":
                    self.run_loader_button.config(state="disabled")
                    self.canvas.itemconfig(self.canvas_text,
                                           text=f"Server Response Code: {response.status_code}"
                                                f"\n Job Id: {response.json()["jobId"]}"
                                                f"\n Job Status: {response.json()["jobStatus"]}"
                                                f"\n Job Result: {response.json()["jobResult"]}")
                else:
                    self.run_loader_button.config(state="normal")
                    self.canvas.itemconfig(self.canvas_text,
                                           text=f"Server Response Code: {response.status_code}"
                                                f"\n Job Id: {response.json()["jobId"]}"
                                                f"\n Job Status: {response.json()["jobStatus"]}"
                                                f"\n Job Result: {response.json()["jobResult"]}")






