import json
import os.path
from tkinter import *
from datetime import timedelta

import pandas
import time
import sys
import book_portico_audit_site_check_bot as book_bot
from trio_websocket import open_websocket
from win32ctypes.pywin32.pywintypes import datetime

from book_portico_audit_site_check_bot import *
from data_handling import base_path

if getattr(sys, 'Frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath("__file__"))

source_file_path = os.path.join(base_path,'source_html')

CONTENT_SET = None
agent = None


def login_in_portico_book_audit_site(username, password):
    #global bot
    global agent
    agent = BookCompletenessCheckerBot(username, password)


def reset_process():
    result = agent.exit_audit_site()
    return result


def start_book_completeness_check(unix_file_path, sheet_name, content_set, result_text, window):
    global CONTENT_SET

    CONTENT_SET = content_set
    counter = 0
    seen_isbn = []
    isbn_found_on_audit = []
    audit_analysis_list = []
    process_start_time  = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)

    data_frame  = pandas.read_excel(unix_file_path, sheet_name)
    result_text.delete("1.0",END)
    # try:
    #     agent.search_provider_on_audit_site(content_set)
    # except TimeoutException:
    #     result_text.insert(END,
    #                        f"Time out Exception book-data-handling.py")
    #     window.update()

    for (index, row) in data_frame.iterrows():
        counter += 1
        result_text.insert(END, f"Processing {counter}/{len(data_frame)} row...\n")
        window.update()
        print(f"Processing {counter}/{len(data_frame)} row...")

        isbn = row.ISBN
        if isbn not in seen_isbn:

            result = agent.search_isbn_on_audit_site(isbn, content_set.rstrip().lstrip())
            # result = agent.find_details_from_source_file(isbn, content_set)
            if result == 501:
                result_text.insert(END, "There is connection problem with the Portico Audit Site. Please try again.\n")
                #print("There is connection problem. Audit site taking time to connect. Please try again.")
                audit_analysis_list.append(f"Try searching again {isbn}")
            elif result ==  400:
                break
            else:
                audit_analysis_list.append(result)
            seen_isbn.append(isbn)
        else:
            result = agent.find_details_from_source_file(isbn, content_set)

    #print(audit_analysis_list)
    agent.exit_audit_site()

    time_stamp = datetime.now().strftime('%d%m%Y%H%M%S')
    try:
        data_frame["ISBN"] = data_frame["ISBN"].astype(str)
        data_frame["Audit_Site_Findings"] = audit_analysis_list

        process_end_time = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second)


        with open(f"{base_path}/log/input_file_details.json", "r") as input_file_details:
            input_information = json.load(input_file_details)
            file_name = input_information["input_file_name"]

        data_frame.to_excel(f"{file_name.replace('.xlsx','')}_{time_stamp}.xlsx")

        lapsed_time = process_end_time - process_start_time
        lapsed_minutes  = int(lapsed_time.total_seconds()//60)
        lapsed_seconds = int(lapsed_time.total_seconds()%60)

        print(f"Analysis completed. Report file path {file_name}_{time_stamp}.xlsx")
        print(f"Total lapsed time: {lapsed_minutes} minutes and {lapsed_seconds} seconds.")

        if os.path.isdir(source_file_path):
            for file in os.listdir(source_file_path):
                file_path = os.path.join(source_file_path, file)
                os.remove(file_path)
                print(f"Deleted [{file_path}] file successfully.")

        result_text.delete("1.0", END)
        result_text.insert(END, f"Total lapsed time: {lapsed_minutes} minutes and {lapsed_seconds} seconds.\nAnalysis is complete.\nReport file path {file_name.replace('.xlsx','')}_{time_stamp}.xlsx\n")

        isbn_under_cs = book_bot.return_found_isbn_under_cs()
        if len(isbn_under_cs) > 0:
            result_text.insert(END,
                               f"\nTotal {len(isbn_under_cs)} ISBN found under the CS {CONTENT_SET}\n")
            for isbn in isbn_under_cs:
                result_text.insert(END, f"{isbn}\n")

        isbn_not_in_Audit = book_bot.return_not_found_in_Audit_site()
        if len(isbn_not_in_Audit) > 0:
            result_text.insert(END,
                               f"\nTotal {len(isbn_not_in_Audit)} ISBN not found in the Audit Site.\n")
            for isbn in isbn_not_in_Audit:
                result_text.insert(END, f"{isbn}\n")

        isbn_under_other_provider = book_bot.return_isbn_found_under_other_provider()

        if len(isbn_under_other_provider) > 0:
            result_text.insert(END,
                               f"\nTotal {len(isbn_under_other_provider)} ISBN  found under the other Provider(s).\n")
            for isbn in isbn_under_other_provider:
                result_text.insert(END, f"{isbn}\n")

        window.update()
    except ValueError:
        pass
    except KeyError:
        result_text.insert(END,
                           f"Wrong Sheet name or input XLSX file selected, please check and Try again.\n")
