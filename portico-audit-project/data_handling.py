import json
import os.path
import sys
import pandas
from tkinter import messagebox
from datetime import *
from datetime import timedelta
from selenium.common import WebDriverException
from log_handling import *
from portico_audit_check_bot import *
from new_portico_audit_site_check_bot import *

AUDIT_URL = "https://audit.portico.org/Portico/login.html"
RESPONSE = None

USER_NAME = ''
PASSWORD = ''
journal_title = None

XSLX_FILE_PATH = ""
SHEET_NAME = ""
bot = None
agent = None

if getattr(sys, 'Frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))


html_folder_path = os.path.join(base_path, "source_html")

def return_error_codes(err_code, journal_title, PROVIDER):
    error_codes = {
        501: f"No result found for [{journal_title}], check for any typo in the journal title or check manually on the Portico Audit Site.",
        502: f"Journal title '{journal_title}' under the provider '{PROVIDER}' is not available. Please check.",
        503: f"Failed to establish a new connection: No connection could be made because the target machine actively refused it"
    }
    return error_codes[err_code]


def login_in_portico_audit_site(username, password):
    #global bot
    global agent
    #bot = PorticoAuditCheckerBot(username, password)
    agent = NewAuditCheckAgent(username, password)

# def login_attempt():
#     try:
#         login_in_portico_audit_site(USER_NAME, PASSWORD)
#     except WebDriverException:
#         messagebox.showinfo("VPN Connection", "Disconnect VPN before running this App.")
#         #print("Disconnect VPN before running this App.")
#     else:
#         start_completeness_check_on_audit_site(XSLX_FILE_PATH, SHEET_NAME)


def start_completeness_check_on_audit_site(xsls_file_path, sheet_name, result_text, window, provider):
    global bot
    try:
        data_frame = pandas.read_excel(xsls_file_path, sheet_name)
        #print(data_frame)
        verified_journal_title = []
        Audit_Findings = []
        title_not_found_on_audit = []

        # Iterating over all rows in the sheet
        quit_driver = False
        item_count = 0

        PROCESS_START_TIME = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)
        #print(PROCESS_START_TIME)

        for (index, row) in data_frame.iterrows():
            #print(row.JOURNAL_TITLE)
            item_count += 1
            if item_count == len(data_frame):
                quit_driver = True

            result_text.delete("1.0", END)
            result_text.insert("1.0", f"Processing {item_count}/{len(data_frame)} row.")
            window.update()
            print(f"Processing {item_count}/{len(data_frame)} row.")

            # Filter out titles which are present on the Audit and which are not.

            if row.JOURNAL_TITLE not in title_not_found_on_audit:
                volume = str(row.VOLUME)

                if volume == 'nan':
                    volume = ''
                else:
                    volume = volume.replace('.0','')

                issue = str(row.ISSUE)

                if issue == 'nan':
                    issue = ''
                else:
                    issue = issue.replace('.0','')

                try:
                    pub_year = str(row.PUBLICATION_YEAR)
                    if pub_year == 'nan':
                        pub_year = ''
                    else:
                        pub_year = pub_year.replace('.0','')
                except AttributeError:
                    pub_year = None

                response = agent.search_journal_title_on_audit_site(journal_title=row.JOURNAL_TITLE, volume=volume, issue=issue, publication_year=pub_year, provider=provider)
                #response = bot.check_journal_title_on_audit(quit_driver, journal_title=row.JOURNAL_TITLE, volume=volume, issue=issue, publication_year=pub_year , provider=provider)

                if response == 501:
                    title_not_found_on_audit.append(row.JOURNAL_TITLE)
                    Audit_Findings.append(return_error_codes(501, row.JOURNAL_TITLE, provider))

                elif response == 502:
                    title_not_found_on_audit.append(row.JOURNAL_TITLE)
                    Audit_Findings.append(return_error_codes(502, row.JOURNAL_TITLE, provider))
                else:
                    Audit_Findings.append(response)

            else:
                # If similar title not found before on the audit site than don't search them again.
                title_not_found_on_audit.append(row.JOURNAL_TITLE)
                Audit_Findings.append(return_error_codes(501, row.JOURNAL_TITLE, provider) + "\n" + return_error_codes(502, row.JOURNAL_TITLE, provider))


        data_frame["Audit_site_findings"] = Audit_Findings

        times_stamp = datetime.now().strftime("%d%m%Y%H%M%S")

        with open(os.path.join(log_folder_path, "input_file_details.json"), "r") as input_file_data:
            file_data = json.load(input_file_data)
            input_file_name = file_data["input_file_name"]

        data_frame.to_excel(f"{input_file_name}_{times_stamp}.xlsx")
        PROCESS_END_TIME = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)

        #print(PROCESS_END_TIME)
        #bot.force_quit_driver()

        TIME_DIFF = PROCESS_START_TIME - PROCESS_END_TIME
        minutes_lapses = int(TIME_DIFF.total_seconds()//60)
        seconds_lapses = int(TIME_DIFF.total_seconds()%60)

        result_text.delete("1.0", END)
        result_text.insert("1.0", f"Time lapse: {abs(minutes_lapses)} minutes and  {seconds_lapses} seconds.\n\n Please check output file [{input_file_name}_{times_stamp}.xlsx]. ")
        if len(title_not_found_on_audit) > 0:
            result_text.insert(END, "\n\n----------------List of Titles not found on the Audit Site------------------------ \n\n")
            for title  in title_not_found_on_audit:
                result_text.insert(END, title + "\n")

        window.update()
        # if os.path.isdir(html_folder_path):
        #     for filename in os.listdir(html_folder_path):
        #         file_path = os.path.join(html_folder_path, filename)
        #         os.remove(file_path)
        #         print(f"File {file_path} deleted successfully.")
    except ValueError:
        result_text.delete("1.0", END)
        result_text.insert(END,
                           "\n\n Error: Please provide correct sheet name from the workbook.")
        window.update()


    # print(f"Please check output file [{input_file_name}_{times_stamp}.xlsx]. Time lapses: {abs(minutes_lapses)} minutes and  {seconds_lapses} seconds.")



