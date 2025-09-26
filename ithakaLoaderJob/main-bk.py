import json
import requests
from tkinter import *
from tkinter import messagebox

# ---------------------------- CONSTANTS ------------------------------- #
FONT_NAME = "Courier"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"


LOADER_ENDPOINT = "http://pr2ptgpprd43.ithaka.org:9500/loader/job/multistepjob/v1/submitwithjsonandparams/LoaderJob"

HEADERS = {
    "accept": "*/*",
    "Content-Type": "application/json",
}

# JSON_DATA = {
#     "configSourceType": "GIT",
#     "propertyFileName": "AMD-Global_Hist_Epidemics-LoaderConfig.properties",
#     "loaderProfileFileName": "AMD-Global_Hist_Epidemics-LoaderProfile.xml"
# }


def save_data():
     property_file_name = propertyFileName_entry.get()
     loader_profile_name = loaderProfileFileName_entry.get()

     if len(property_file_name) == 0:
         messagebox.showinfo("Property File", "Property File Name is missing..")
     elif len(loader_profile_name) == 0:
         messagebox.showinfo("Loader Profile", "Loader Profile Name is missing..")
     else:
         JSON_DATA = {
             "configSourceType": "GIT",
             "propertyFileName": property_file_name,
             "loaderProfileFileName": loader_profile_name
         }

         with open("loader_config.json", "w") as config_file:
             json.dump(JSON_DATA, config_file, indent=4)

         run_loader(JSON_DATA)


def run_loader(json_data):
    loader_run_response = requests.post(LOADER_ENDPOINT, json=json_data, headers=HEADERS)
    #print(loader_run_response.json()["jobId"])
    loader_response_data = {
        "jobId" : loader_run_response.json()["jobId"]
    }

    with open("job_id.json", "w") as job_id_file:
        json.dump(loader_response_data, job_id_file, indent=4)

    canvas.itemconfig(canvas_text, text=f"Job Status: {loader_run_response.json()['jobStatus']}\n Job Id: {loader_response_data['jobId']}")


def check_job_status():

    with open("job_id.json", "r") as job_id_file:
        data = json.load(job_id_file)
        JOB_ID = data['jobId']

    LOADER_JOB_STATUS_ENDPOINT = f"http://pr2ptgpprd43.ithaka.org:9500/loader/job/v1/status/{JOB_ID}"

    job_response = requests.get(LOADER_JOB_STATUS_ENDPOINT)

    if job_response.json()["jobResult"] == "EXECUTING":
        run_loader_button.config(state="disabled")
    else:
        run_loader_button.config(state="normal")

    try:
        job_response.raise_for_status()
    except Exception:
        canvas.itemconfig(canvas_text, text=f"Status Code: {job_response.status_code}\n"
                                            f"JOB ID: {job_response.json()["jobId"]}"
                          f"JOB NAME: {job_response.json()["jobName"]} \n JOB RESULT: {job_response.json()["jobResult"]}")
    else:
        canvas.itemconfig(canvas_text, text=f"Status Code: {job_response.status_code}\n"
                                            f" JOB ID: {job_response.json()["jobId"]}"
                                            f" JOB NAME: {job_response.json()["jobName"]} \n JOB RESULT: {job_response.json()["jobResult"]}")



# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
window.title("Ithaka Loader - Workbench")
window.config(padx=50, pady=50)


propertyFileName_label = Label(text="Property File Name: ")
propertyFileName_label.grid(row=0, column=0)
propertyFileName_label.config(padx=10, pady=10)


loaderProfileFileName_label = Label(text="Loader Profile Name: ")
loaderProfileFileName_label.grid(row=1, column=0)
loaderProfileFileName_label.config(padx=10, pady=10)

propertyFileName_entry = Entry(width=35)
propertyFileName_entry.grid(row=0, column=1, columnspan=2)

loaderProfileFileName_entry = Entry(width=35)
loaderProfileFileName_entry.grid(row=1, column=1, columnspan=2)

run_loader_button = Button(text="Run Loader", highlightthickness=0, command=save_data)
run_loader_button.grid(row=3, column=1)

canvas = Canvas(height=100, width=300)
canvas.grid(row=4, column=0, columnspan=3)
canvas_text = canvas.create_text(150,30, text="Loader - Workbench", font=(FONT_NAME, 10, "italic"))

check_status_button = Button(text="Check Job Status", highlightthickness=0, command=check_job_status)
check_status_button.grid(row=5, column=1)
window.mainloop()