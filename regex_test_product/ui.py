import os.path
import tkinter
from gc import collect
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import re
import json
from tkinter.filedialog import askopenfile, askopenfilename
from xml.etree.ElementTree import ElementTree
import lxml
from bs4 import BeautifulSoup
import xml.etree.ElementTree
import jenkins_ui
import jenkins_build

FONT_NAME = "calibre"
BACKGROUND_COLOR = "#B1DDC6"
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"



class UI:
    def __init__(self):
        self.input_text_list = []
        self.IP_IDS = []
        self.IP_REGEX = []

        self.FR_IDS = []
        self.FR_REGEX = []

        self.EX_FR_IDS = []
        self.EX_FR_REGEX = []

        self.DR_IDS = []
        self.DR_REGEX = []

        self.FILE_NAME = None

        self.regex_window = Tk()
        self.regex_window.title("Regex Testing Tool")
        #self.window.geometry("800x600")
        self.regex_window.minsize(height=700, width=1200)
        self.regex_window.config(padx=10, pady=10)

        # Allows resizing in both width and height
        self.regex_window.resizable(False, False)

        # self.window.rowconfigure(0, weight=1)
        # self.window.columnconfigure(0, weight=1)
        self.frame_1 = Frame(self.regex_window, bg=YELLOW)
        self.frame_1.grid(row=0, column=0, columnspan=5)

        self.frame_2 = Frame(self.regex_window, bg=YELLOW)
        self.frame_2.grid(row=5, column=0, columnspan=5)

        self.frame_3 = Frame(self.regex_window, bg=YELLOW)
        self.frame_3.grid(row=3, column=0, columnspan=5)

        self.load_from_file = Button(self.frame_1, text="Load Profile", pady=5, command=self.choose_file, font=(FONT_NAME, 10, "bold"))
        self.load_from_file.grid(row=0, column=0, padx=10)

        self.file_name_canvas = Canvas(self.frame_1,  height=10, width=300)
        self.file_name_canvas_text = self.file_name_canvas.create_text(150, 7, text="No File selected..", font=(FONT_NAME, 10, "italic"))
        self.file_name_canvas.grid(row=0, column=1, padx=5)

        # self.yScroll = Scrollbar(orient=VERTICAL)
        # self.yScroll.grid(row=0, column=2)

        # ListBox for IP rules
        self.ip_rules_list = Listbox(self.frame_1, height=2)
        self.ip_rules_list.grid(row=0, column=2, padx=10)
        self.ip_rules_list.bind("<<ListboxSelect>>",self.get_ip_regex)

        # ListBox for FR rules
        self.fr_rules_list = Listbox(self.frame_1, height=2)
        self.fr_rules_list.grid(row=0, column=3, padx=10)
        self.fr_rules_list.bind("<<ListboxSelect>>",self.get_fr_regex)

        # ListBox for DR rules

        self.dr_rules_list = Listbox(self.frame_1, height=2)
        self.dr_rules_list.grid(row=0, column=4, padx=10)
        self.dr_rules_list.bind("<<ListboxSelect>>", self.get_dr_regex)

        self.fer_rules_list = Listbox(self.frame_1, height=2)
        self.fer_rules_list.grid(row=0, column=5, padx=10)
        self.fer_rules_list.bind("<<ListboxSelect>>", self.get_fer_regex)


        self.input_label = Label(text="Input Text(s)", font=(FONT_NAME, 10, "bold"), padx=10, pady=10)
        self.input_label.grid(row=1, column=0)

        self.jenkins_button = Button(text="Launch Jenkins", font=(FONT_NAME, 10, "bold"), padx=10, pady=10, command=lambda : jenkins_ui.jenkins_module())
        self.jenkins_button.grid(row=1, column=5)


        self.input_text = Text(height=13, width=120, padx=10, pady=10)
        self.input_text.grid(row=2, column=0, columnspan=3, rowspan=1)

        self.regex_strings_label = Label(self.frame_3, text="Regext Pattern Text", font=(FONT_NAME, 10, "bold"), padx=20, pady=20)
        self.regex_strings_label.grid(row=0, column=0)

        self.checked_state_variable = IntVar()

        self.ignore_case_check_box = Checkbutton(self.frame_3, text="Ignore Case", variable=self.checked_state_variable, font=(FONT_NAME, 10, "italic"))
        self.ignore_case_check_box.grid(row=0, column=1)

        self.regex_pattern_canvas = Canvas(self.frame_3, height=10, width=700, bg=YELLOW)
        self.regex_pattern_canvas_text = self.regex_pattern_canvas.create_text(200, 7, text=" ", font=(FONT_NAME, 10, "italic"))
        self.regex_pattern_canvas.grid(row=0, column=2)

        self.regex_text_area = Text(height=3, width=120, undo=True)
        self.regex_text_area.grid(row=4, column=0, columnspan=3, rowspan=1)

        self.result_label = Label(self.frame_2, text="Result", font=(FONT_NAME, 10, "bold"), padx=20, pady=20)
        self.result_label.grid(row=0, column=0)

        self.status_canvas  = Canvas(self.frame_2, height=40, width=800, bg=YELLOW)
        self.canvas_text = self.status_canvas.create_text(200, 20, text="Press Execute button to Test", font=(FONT_NAME, 10, "italic"))
        self.status_canvas.grid(row=0, column=1)

        self.result_text = Text(height=15, width=120, padx=10, pady=10)
        self.result_text.grid(row=6, column=0, columnspan=3, rowspan=1)

        self.blank_label = Label(text=" ")
        self.blank_label.grid(row=2, column=4)

        self.blank_label1 = Label(text=" ")
        self.blank_label1.grid(row=4, column=4)

        self.blank_label2 = Label(text=" ")
        self.blank_label2.grid(row=6, column=4)

        self.trim_input_string = Button(text="Remove Space", padx=10, pady=10, command=self.remove_space, font=(FONT_NAME, 10, "bold"))
        self.trim_input_string.grid(row=2, column=5)

        self.execute_regex = Button(text="Execute Regex", padx=10, pady=10, command=self.execute_regex, font=(FONT_NAME, 10, "bold"))
        self.execute_regex.grid(row=4, column=5)

        self.reset_all = Button(text="Reset", padx=30, pady=10, command=self.reset_text, font=(FONT_NAME, 10, "bold"))
        self.reset_all.grid(row=6, column=5)

        try:
            if open(os.path.join(jenkins_build.log_folder_path, "file_name.json"), "r"):
                self.load_choosed_file()
        except FileNotFoundError:
            pass

        self.load_data()
        self.regex_window.mainloop()

    def clear_all_list(self):
        self.ip_rules_list.delete(first=0, last=len(self.IP_IDS)-1)
        self.IP_IDS.clear()
        self.IP_REGEX.clear()

        self.fr_rules_list.delete(first=0, last=len(self.FR_IDS)-1)
        self.FR_IDS.clear()
        self.FR_REGEX.clear()

        self.fer_rules_list.delete(first=0, last=len(self.EX_FR_IDS)-1)
        self.EX_FR_IDS.clear()
        self.EX_FR_REGEX.clear()

        self.dr_rules_list.delete(first=0, last=len(self.DR_IDS)-1)
        self.DR_IDS.clear()
        self.DR_REGEX.clear()

    def print_all_list(self):
        print(self.IP_IDS)
        print(self.IP_REGEX)
        print(self.FR_IDS)
        print(self.FR_REGEX)
        print(self.EX_FR_IDS)
        print(self.EX_FR_REGEX)
        print(self.DR_IDS)
        print(self.DR_REGEX)

    def get_dr_regex(self, event):
        try:
            item = self.dr_rules_list.get(self.dr_rules_list.curselection())
            self.regex_text_area.delete("1.0", END)
            self.regex_text_area.insert("1.0", self.DR_REGEX[self.DR_IDS.index(item)])
        except TclError:
            pass

    def get_fer_regex(self, event):
        try:
            item = self.fer_rules_list.get(self.fer_rules_list.curselection())
            self.regex_text_area.delete("1.0", END)
            self.regex_text_area.insert("1.0", self.EX_FR_REGEX[self.EX_FR_IDS.index(item)])
        except TclError:
            pass


    def get_fr_regex(self, event):
        try:
            item = self.fr_rules_list.get(self.fr_rules_list.curselection())
            self.regex_text_area.delete("1.0", END)
            self.regex_text_area.insert("1.0", self.FR_REGEX[self.FR_IDS.index(item)])
        except TclError:
            pass

    def get_ip_regex(self, event):
        try:
            item = self.ip_rules_list.get(self.ip_rules_list.curselection())
            #print(self.IP_REGEX[self.IP_IDS.index(item)])
            self.regex_text_area.delete("1.0", END)
            self.regex_text_area.insert("1.0", self.IP_REGEX[self.IP_IDS.index(item)])
        except TclError:
            pass

    def choose_file(self):
        file_path = askopenfilename()
        unix_file_path = file_path.replace('C:', '').replace('\\', '/')

        with open(os.path.join(jenkins_build.log_folder_path, "file_name.json"), "w") as file_details:
            new_file_path = {
                "file_name": unix_file_path
            }
            json.dump(new_file_path, file_details, indent=4)

        # print(unix_file_path)
        #print(file_path.split('/')[-1])
        self.file_name_canvas.itemconfig(self.file_name_canvas_text, text=file_path.split('/')[-1], font=(FONT_NAME, 10, "italic"))

        try:
            with open(unix_file_path, 'r') as data_file:
                content = data_file.read()
        except FileNotFoundError:
            pass
        else:
            self.clear_all_list()
            #self.print_all_list()

            #print(content)
            soup = BeautifulSoup(content, "lxml-xml")
            # print(soup.InterpretPackagingRuleSet.PatternRule.ComplexPattern.CapturePattern)
            ip_pattern_rules = soup.select("InterpretPackagingRuleSet PatternRule")
            #print(pattern_rules)
            self.IP_IDS = [rule.get("RuleId") for rule in ip_pattern_rules]

            for id in self.IP_IDS:
                self.ip_rules_list.insert(self.IP_IDS.index(id), id)

            ip_pattern_capture_patterns = soup.select("InterpretPackagingRuleSet PatternRule ComplexPattern CapturePattern")
            self.IP_REGEX = [regex.getText() for regex in ip_pattern_capture_patterns]

            fr_patterns_ruleId = soup.select("FileReferenceResolutionRuleSet FileReferenceResolutionRule")
            self.FR_IDS = [frid.get("RuleId") for frid in fr_patterns_ruleId]

            fr_patterns_regex = soup.select("FileReferenceResolutionRuleSet FileReferenceResolutionRule CapturePattern")
            self.FR_REGEX = [pattern.getText() for pattern in fr_patterns_regex]

            for id in self.FR_IDS:
                self.fr_rules_list.insert(self.FR_IDS.index(id), id)

            dr_patterns_ruleId = soup.select("DelayerRuleSet PatternRule")
            self.DR_IDS = [rule.get('RuleId') for rule in dr_patterns_ruleId]
            self.DR_REGEX.clear()
            dr_patterns_regex = soup.select("DelayerRuleSet PatternRule SimplePattern")
            self.DR_REGEX = [rule.getText() for rule in dr_patterns_regex]

            for id in self.DR_IDS:
                self.dr_rules_list.insert(self.DR_IDS.index(id), id)

            ex_fr_patterns_ruleId = soup.select("ExcludeUnreferencedFileRuleSet ExcludeUnreferencedFileRule")
            self.EX_FR_IDS = [rule.get('RuleId') for rule in ex_fr_patterns_ruleId]

            ex_fr_patterns_regex = soup.select("ExcludeUnreferencedFileRuleSet ExcludeUnreferencedFileRule Pattern")
            self.EX_FR_REGEX = [rule.getText() for rule in ex_fr_patterns_regex]

            for id in self.EX_FR_IDS:
                self.fer_rules_list.insert(self.EX_FR_IDS.index(id), id)



    def load_choosed_file(self):
        try:
            with open(os.path.join(jenkins_build.log_folder_path, "file_name.json")) as file_path:
                file_path = json.load(file_path)
        except FileNotFoundError:
            pass
        else:
            self.clear_all_list()
            unix_file_path = file_path["file_name"].replace('C:', '').replace('\\', '/')
            self.file_name_canvas.itemconfig(self.file_name_canvas_text, text=file_path["file_name"].split('/')[-1], font=(FONT_NAME, 10, "italic"))

            try:
                with open(unix_file_path, 'r') as data_file:
                    content = data_file.read()
            except FileNotFoundError:
                pass
            else:
                #print(content)
                soup = BeautifulSoup(content, "lxml-xml")
                # print(soup.InterpretPackagingRuleSet.PatternRule.ComplexPattern.CapturePattern)
                ip_pattern_rules = soup.select("InterpretPackagingRuleSet PatternRule")
                #print(pattern_rules)
                self.IP_IDS = [rule.get("RuleId") for rule in ip_pattern_rules]

                for id in self.IP_IDS:
                    self.ip_rules_list.insert(self.IP_IDS.index(id), id)

                ip_pattern_capture_patterns = soup.select("InterpretPackagingRuleSet PatternRule ComplexPattern CapturePattern")
                self.IP_REGEX = [regex.getText() for regex in ip_pattern_capture_patterns]

                fr_patterns_ruleId = soup.select("FileReferenceResolutionRuleSet FileReferenceResolutionRule")
                self.FR_IDS = [frid.get("RuleId") for frid in fr_patterns_ruleId]

                fr_patterns_regex = soup.select("FileReferenceResolutionRuleSet FileReferenceResolutionRule CapturePattern")
                self.FR_REGEX = [pattern.getText() for pattern in fr_patterns_regex]

                for id in self.FR_IDS:
                    self.fr_rules_list.insert(self.FR_IDS.index(id), id)

                dr_patterns_ruleId = soup.select("DelayerRuleSet PatternRule")
                self.DR_IDS = [rule.get('RuleId') for rule in dr_patterns_ruleId]

                dr_patterns_regex = soup.select("DelayerRuleSet PatternRule SimplePattern")
                self.DR_REGEX = [rule.getText() for rule in dr_patterns_regex]

                for id in self.DR_IDS:
                    self.dr_rules_list.insert(self.DR_IDS.index(id), id)

                ex_fr_patterns_ruleId = soup.select("ExcludeUnreferencedFileRuleSet ExcludeUnreferencedFileRule")
                self.EX_FR_IDS = [rule.get('RuleId') for rule in ex_fr_patterns_ruleId]

                ex_fr_patterns_regex = soup.select("ExcludeUnreferencedFileRuleSet ExcludeUnreferencedFileRule Pattern")
                self.EX_FR_REGEX = [rule.getText() for rule in ex_fr_patterns_regex]

                for id in self.EX_FR_IDS:
                    self.fer_rules_list.insert(self.EX_FR_IDS.index(id), id)



    def check_box_status(self):
        pass
        #print(self.checked_state_variable.get())

    def reset_text(self):
        #self.file_name_canvas.itemconfig(self.file_name_canvas_text, text="No file selected..")
        self.status_canvas.itemconfig(self.canvas_text, text="Press Execute button to test regex pattern.", font=(FONT_NAME, 10, "italic"))
        self.input_text.delete("1.0", END)
        self.regex_text_area.delete("1.0", END)
        self.result_text.delete("1.0", END)

    def load_data(self):

        try:
            with open(os.path.join(jenkins_build.log_folder_path, "data.json"), "r") as data_file:
                contents = json.load(data_file)
                row_no = 0
                for input_string in contents["Input Data"]:
                    row_no +=1
                    self.input_text.insert(f"{row_no}.0", input_string + "\n")
                self.input_text_list = contents["Input Data"]
                self.regex_text_area.insert("1.0", contents["Regex String"])

        except FileNotFoundError:
            pass



    def remove_space(self):
        content = self.input_text.get("1.0", END)
        # print(content)
        tab_free_content = re.sub(r'[\t]+', '', content)
        # print(tab_free_content)
        new_line_free_content = re.sub(r'\n[\n]+','\n', tab_free_content)
        # print(new_line_free_content)
        #space_free_content = re.sub(r'                        ','', tab_free_content)
        space_free_content = re.sub(r'^\s+', '', tab_free_content, flags=re.MULTILINE)
        #newline_space_free_content = re.sub(r'\n\s+', '\n', space_free_content)
        #print(space_free_content)
        self.input_text.delete("1.0", END)
        self.input_text.insert(END, space_free_content)
        self.input_text_list = [string.strip('') for string in new_line_free_content.split('\n') if len(string) > 0]



    def execute_regex(self):
        if self.regex_text_area.get("1.0", END).strip() == '':
            messagebox.showinfo("Regex Error", "Regex String can't be empty..")
        elif self.input_text.get("1.0", END).strip() == '':
            messagebox.showinfo("Input Strings Error", "Input Strings can't be empty..")

        else:
            # self.regex_text_area.insert(END, f"No of input to match {len(self.input_text_list)}")
            self.remove_space()
            regex_string = self.regex_text_area.get("1.0", END).strip()

            with open(os.path.join(jenkins_build.log_folder_path, "data.json"), "w") as data_file:
                data = {
                    "Input Data" : self.input_text_list,
                    "Regex String": regex_string

                }
                json.dump(data, data_file, indent=4)

            try:
                re.compile(regex_string)
                self.regex_pattern_canvas.itemconfig(self.regex_pattern_canvas_text, text="Pattern is valid.", font=(FONT_NAME, 10, "italic"))
            except re.PatternError as e:
                self.regex_pattern_canvas.itemconfig(self.regex_pattern_canvas_text, text=f"Pattern is not valid [{e}]",
                                                     font=(FONT_NAME, 10, "italic"))


            self.result_text.delete("1.0", END)
            row_no = 0
            input_str_counter = 0
            test_cases = len(self.input_text_list)
            matched_cases = 0
            unmatched_cases = 0

            for input_str in self.input_text_list:
                input_str_counter += 1
                #print(input_str)
                # result_string = regex.match(input_str)
                if self.checked_state_variable.get() == 1:
                    result_string = re.search(regex_string, input_str, flags=re.IGNORECASE)
                else:
                    result_string = re.search(regex_string, input_str)
                # print("*",result_string)
                # print("**", result_string.re)

                row_no += 1
                grp_no = 0
                #self.result_text.insert(f"{str(row_no)}.0",f"Matched String: {result_string.groups()}\n")
                if result_string is not None:
                    matched_cases += 1
                    self.result_text.insert(f"{row_no}.0", f"Input String {input_str_counter} ==> " + result_string.string + "\n" * 2 )

                    for grp in result_string.groups():
                        row_no += 2
                        self.result_text.insert(f"{str(row_no)}.0", f"Group {grp_no}: {grp}\n")
                        grp_no += 1
                    row_no +=2
                    self.result_text.insert(f"{row_no}.0", "+----+" * 20 + "\n")
                else:
                    unmatched_cases += 1
                    self.result_text.insert(f"{row_no}.0",f"Input String {input_str_counter}: {input_str} ==> Did not matched. \n  {'+----+' * 20}  \n")
                    row_no += 2

            self.status_canvas.itemconfig(self.canvas_text, text=f"Test Cases: {test_cases} | Matched Cases: {matched_cases} | Unmatched Cases: {unmatched_cases} ", font=(FONT_NAME, 10, "italic"))



