""" IM-FIT """

#!/usr/bin/env python3

import os
import re
import sys
import time
import ast
import json
import subprocess
import xml.etree.ElementTree as ET
import random
import pytest
import astunparse

from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from PySide6 import *

from modules import *
from widgets import *

from ui_main import Ui_MainWindow

import IMFIT_functions
import dbConnection

import scan_process
import monitoring_process


class MainWindow(QMainWindow):
    """IM-FIT UI Window"""

    global RUN_ORDER_LIST_JUST_PATH
    RUN_ORDER_LIST_JUST_PATH = []

    global ROS_SOURCE_CODE
    ROS_SOURCE_CODE = ""

    global POSSIBLE_MUTANT_LIST
    POSSIBLE_MUTANT_LIST = []

    global ZIPPED_LIST
    ZIPPED_LIST = []

    global ZIPPED_ROS_LIST
    ZIPPED_ROS_LIST = []

    global ROS_SOURCE_MUTANT
    ROS_SOURCE_MUTANT = []

    global source_and_mutate_code
    source_and_mutate_code = []

    global fault_name_list
    fault_name_list = []

    global fi_plan_directory_list
    fi_plan_directory_list = []

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        #  APP NAME
        title = "IM-FIT"
        description = "IM-FIT"

        #  APPLY TEXTS
        self.setWindowTitle(title)
        self.ui.titleRightInfo.setText(description)

        # TOGGLE MENU
        self.ui.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        UIFunctions.uiDefinitions(self)

        # DATA
        self.code_part_for_mutation = []

        ### FUNCTIONS

        ### TAKE FILE FUNCTIONS

        # Take ".py" file for source code
        def get_file_py_for_source_code():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.py"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                # .py file is choosed by the user
                if file_name[0].endswith(".py") or file_name[0].endswith(".txt"):
                    # file_name[0] is directory of file
                    with open(file_name[0], mode="r", encoding="utf-8") as json_file:
                        source_code_data = json_file.read()
                        # Source code directory is added to the text
                        self.ui.source_code_directory_text.setPlainText(
                            str(file_name[0])
                        )
                        self.ui.source_code_content.setPlainText(source_code_data)

        # Take ".py" file for test case
        def get_file_py_for_test_case():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.py"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                if file_name[0].endswith(".py"):
                    with open(file_name[0], mode="r", encoding="utf-8") as json_file:
                        data = json_file.read()
                        self.ui.test_case_directory_text.setPlainText(str(file_name[0]))
                        self.ui.test_case_content.setPlainText(data)

        # Take ".json" file for workload
        def workload_get_file_json():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.json"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()

                if file_name[0].endswith(".json"):
                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()
                        self.ui.textEdit_46.setPlainText(str(file_name[0]))
                        self.ui.textEdit_3.setPlainText(data)

        # Take ".json" file function
        def fiplan_get_file_json():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.json"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()

                if file_name[0].endswith(".json"):
                    self.ui.listWidget_11.addItem(str(file_name[0]))

        def get_file_json_for_workload():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.json"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()

                if file_name[0].endswith(".json"):
                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()
                        self.ui.textEdit_3.setPlainText(data)

        # Take ".rosbag" file function
        def get_file_rosbag():
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.bag"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()

                if file_name[0].endswith(".bag"):
                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()
                        self.ui.textEditor.setPlainText(data)

        # EDIT BUTTONS

        # Source Code Edit Checkbox on START PAGE
        def edit_source_code():
            if self.ui.checkBox_8.isChecked() is True:
                self.ui.source_code_content.setReadOnly(False)
            else:
                self.ui.source_code_content.setReadOnly(True)

        # Workload Edit Checkbox on START PAGE
        def edit_workload():
            if self.ui.checkBox_5.isChecked() is True:
                self.ui.textEdit_3.setReadOnly(False)
            else:
                self.ui.textEdit_3.setReadOnly(True)

        # Select Code Snippets wit One Click
        def code_snippet_select_with_one_clicked():
            try:
                clicked_item_text = self.ui.code_snippet_list.currentItem().text()

                with open(
                    "code_snippets.json", encoding="utf-8"
                ) as code_snippets_from_json:
                    code_snippets_name_list = json.load(code_snippets_from_json)

                    added_snippet_regex_length = len(
                        code_snippets_name_list["code_snippets"]
                    )
                    for i in range(0, added_snippet_regex_length):
                        code_snippet_name = code_snippets_name_list["code_snippets"][i][
                            "Snippets"
                        ]["Snippet_Name"]

                        if clicked_item_text == code_snippet_name:
                            code_snippet_description = code_snippets_name_list[
                                "code_snippets"
                            ][i]["Snippets"]["Process"]
                            self.ui.textEdit_24.setPlainText(code_snippet_description)
            except AttributeError:
                pass

        # Select Snippet Button on Start Page
        def code_snippet_selection():
            code_snippet_list_is_empty = True

            len_of_selected_code_snippets = self.ui.listWidget_8.count()

            selected_row = self.ui.code_snippet_list.currentItem().text()
            row = selected_row.split("\n")

            ### Check Double Enter
            if len_of_selected_code_snippets:
                for i in range(len_of_selected_code_snippets):
                    code_snippet_list_element = self.ui.listWidget_8.item(i).text()
                    if code_snippet_list_element == selected_row:
                        code_snippet_list_is_empty = False

                if code_snippet_list_is_empty is True:
                    self.ui.listWidget_8.addItems(row)
            else:
                self.ui.listWidget_8.addItems(row)

        # Select Task on Create on Workload Page
        def task_selection():
            selected_row = self.ui.listWidget_21.currentItem().text()
            row = selected_row.split("\n")
            self.ui.listWidget_22.addItems(row)

        # Select Task with One Click on Workload Page
        def task_info_with_one_click():
            clicked_item_text = self.ui.listWidget_21.currentItem().text()
            self.ui.textEdit_14.clear()

            json_type_task = self.ui.plainTextEdit.toPlainText()
            tasks_list_json = json.loads(json_type_task)

            for i in range(0, len(tasks_list_json["Tasks"])):
                task_name = str(tasks_list_json["Tasks"][i]["Task"]["Task_ID"])
                if task_name == clicked_item_text:
                    task_detail = str(tasks_list_json["Tasks"][i]["Task"])
                    for j in task_detail:
                        self.ui.textEdit_14.setPlainText(
                            self.ui.textEdit_14.toPlainText() + j
                        )

        def possible_mutation_line_selection():
            """Select Line For Mutation on FI Plan Page"""
            possible_mutation_line = self.ui.listWidget.currentItem().text()
            self.ui.textEdit_13.setPlainText(possible_mutation_line)

        def fault_selection_from_library():
            """Select Fault From Fault Library on FI Plan Page"""
            global ZIPPED_LIST
            ZIPPED_LIST = []

            text_check = self.ui.textEdit_13.toPlainText()

            if text_check:

                selected_line = self.ui.textEdit_13.toPlainText()
                selected_fault = self.ui.listWidget_3.currentItem().text()

                text_selected_line_and_fault = (
                    selected_line + " #==># " + selected_fault
                )

                ZIPPED_LIST.append(text_selected_line_and_fault)

                line_and_fault = text_selected_line_and_fault.split("\n")

                self.ui.listWidget_7.addItems(line_and_fault)

        # This Function Shows Fault's Information from Fault Library on FI Plan Page
        def show_fault_info_with_one_click():
            try:
                clicked_item_text = self.ui.listWidget_3.currentItem().text()

                with open("faultLibrary.json", encoding="utf-8") as file:
                    fault_list = json.load(file)

                fault_list_size = self.ui.listWidget_3.count()

                for i in range(fault_list_size):
                    fault_name = fault_list["all_faults"][i]["fault"]["Fault_Name"]

                    if clicked_item_text == fault_name:
                        fault_description = fault_list["all_faults"][i]["fault"][
                            "Explanation"
                        ]
                        self.ui.textEdit_17.setPlainText(fault_description)
            except:
                IndexError()

        def nth_replace(string, old, new, replace_num=1):
            """Replace Funtion"""

            left_join = old
            right_join = old
            groups = string.split(old)
            nth_split = [
                left_join.join(groups[:replace_num]),
                right_join.join(groups[replace_num:]),
            ]
            return new.join(nth_split)

        def mutation_process_function(target_text, start_json_value, finish_json_value):
            global source_and_mutate_code
            source_and_mutate_code = []

            # try:
            # Fault Lİbrary JSON is opened
            with open("faultLibrary.json", encoding="utf-8") as file:
                fault_list = json.load(file)

            for fault_number in range(start_json_value, finish_json_value):
                target_operators_from_library = fault_list["all_faults"][fault_number][
                    "fault"
                ]["Target_to_Change"]
                operators = target_operators_from_library.split(",")

                changed_operators_from_library = fault_list["all_faults"][fault_number][
                    "fault"
                ]["Changed"]
                split_operators = changed_operators_from_library.split(",")
                for k in operators:
                    find_k_in_text = re.findall(k, target_text)
                    if find_k_in_text:
                        found_target = find_k_in_text[0]
                        number_of_pattern = len(find_k_in_text)
                        for changing_number in range(1, number_of_pattern + 1):
                            for changed_line in split_operators:
                                mutated_line = nth_replace(
                                    target_text,
                                    found_target,
                                    changed_line,
                                    replace_num=changing_number,
                                )
                                if mutated_line != target_text:
                                    # Mutated line is added to mutation list on IM-FIT UI
                                    self.ui.listWidget_4.addItem(mutated_line)
                                    # Original source code line and mutated line are added to
                                    # list to use for execution
                                    source_and_mutate_code.append(target_text)
                                    source_and_mutate_code.append(mutated_line)
                                else:
                                    continue

            total_mut = self.ui.listWidget_4.count()
            self.ui.label_17.setText(str(total_mut))
            # except:
            #     message_box = QMessageBox()
            #     message_box.setIcon(QMessageBox.Critical)
            #     message_box.setText("Failed to create mutant!")
            #     message_box.setWindowTitle("Caution!")
            #     message_box.setStandardButtons(QMessageBox.Ok)
            #     message_box.exec()

        def fault_lib_size():
            with open("faultLibrary.json", encoding="utf-8") as file:
                fault_list = json.load(file)
            fault_library_size = len(fault_list["all_faults"])
            return fault_library_size

        def basla_func():
            with open("faultLibrary.json", encoding="utf-8") as file:
                fault_list = json.load(file)
            fault_library_size = fault_lib_size()
            if self.ui.checkBox_4.isChecked() is True:
                len_selected_line_mutation = self.ui.listWidget.count()
                for i in range(0, len_selected_line_mutation):
                    line = self.ui.listWidget.item(i).text()
                    mutation_process_function(line, 0, fault_library_size)
            else:
                len_selected_line_mutation = self.ui.listWidget_7.count()
                for i in range(0, len_selected_line_mutation):
                    hata_ve_line = self.ui.listWidget_7.item(i).text()
                    split_hata_ve_line = hata_ve_line.split(" #==># ")
                    hata_ismi = split_hata_ve_line[1]
                    line = split_hata_ve_line[0]
                    for fault_number in range(fault_library_size):
                        fault_name_from_library = fault_list["all_faults"][
                            fault_number
                        ]["fault"]["Fault_Name"]
                        if hata_ismi == fault_name_from_library:
                            mutation_process_function(
                                line, fault_number, fault_number + 1
                            )

        def random_hata_bas():
            fault_library_size = fault_lib_size()
            random_fault = random.randint(0, fault_library_size)
            target_text = self.ui.listWidget.currentItem().text()
            mutation_process_function(target_text, random_fault, random_fault + 1)

        def execution_module_function():
            global ROS_SOURCE_MUTANT
            global ROS_SOURCE_CODE
            ROS_SOURCE_MUTANT = []
            ROS_SOURCE_CODE = []

            killed_mutants_list = []
            survived_mutants_list = []
            equivalent_mutants_list = []

            error_code_list = []

            killed_mutants = 0
            survivor_mutants = 0
            equivalent_mutants = 0
            fault_name_list = []
            execution_timeout_list = []
            original_source_code_output = ""

            execution_fiplan_list_length = self.ui.listWidget_6.count()

            for execution_step in range(0, execution_fiplan_list_length):
                execution_fiplan_directory = self.ui.listWidget_6.item(
                    execution_step
                ).text()
                file_type_keywords = [
                    "_type_python.json",
                    "_type_launch.json",
                    "_type_rospy.json",
                ]
                for file_type_pattern in file_type_keywords:
                    find_file_type = re.findall(
                        file_type_pattern, execution_fiplan_directory
                    )
                    if find_file_type:
                        # ROS-Py execution settings
                        if find_file_type[0] == "_type_rospy.json":

                            killed_counter = 0
                            survived_counter = 0

                            # Length of ROS source mutant list
                            len_ros_source_mutant = len(ROS_SOURCE_MUTANT)

                            working_directory = self.ui.textEdit_47.toPlainText()

                            for i in range(len_ros_source_mutant):
                                if i % 2 == 1:
                                    new_data = ROS_SOURCE_CODE.replace(
                                        ROS_SOURCE_MUTANT[i - 1], ROS_SOURCE_MUTANT[i]
                                    )

                                    fname = "mutant" + str(int(i / 2)) + ".py"

                                    complete_name = os.path.join(
                                        working_directory, fname
                                    )

                                    with open(
                                        complete_name, mode="w", encoding="utf-8"
                                    ) as file1:
                                        file1.write(new_data)

                                    subprocess.Popen(
                                        ["chmod", "+x", fname], cwd=working_directory
                                    )

                                    print("\n\n############")
                                    print("Mutant:", fname)
                                    print("#" * 10)

                                    try:
                                        roscore_process = subprocess.Popen(["roscore"])
                                        time.sleep(5)
                                        status_output = subprocess.Popen(
                                            ["rosrun", "deneme_paket", fname]
                                        )
                                        status_output.wait(timeout=5)
                                    except subprocess.TimeoutExpired:
                                        status_output.terminate()
                                        roscore_process.terminate()
                                        survived_counter += 1
                                        print("#" * 10)
                                        print("#       Survived Mutant          #")
                                        print("#" * 10)
                                        print("\n\n")
                                        print("-" * 10)
                                    else:
                                        status_output.terminate()
                                        roscore_process.terminate()
                                        killed_counter += 1
                                        print("#" * 10)
                                        print("#     Killed Mutant            #")
                                        print("#" * 10)
                                        print("\n\n")
                                        print("" - "*10")
                            print("\n\n############")
                            print("#       Results            #")
                            print("#" * 10)
                            print("\n\n")

                            print("Total Killed Mutant(s):", killed_counter)
                            print("Total Survived Mutant(s):", survived_counter)

                            print(
                                "\nMutation Score:",
                                (killed_counter / (killed_counter + survived_counter))
                                * 100,
                            )

                            print("" - "*10\n\n")

                        elif find_file_type[0] == "_type_launch.json":
                            killed_counter = 0
                            survived_counter = 0

                            fiplan_directory = self.ui.listWidget_36.item(0).text()
                            with open(fiplan_directory, encoding="utf-8") as json_file:
                                fault_list = json.load(json_file)

                            for i in range(len(fault_list)):
                                directory = fault_list[i]["Fault"]["File_Directory"]

                                split_directory = directory.split("/")
                                folder_name = split_directory[-3]

                                ros_exe_file_name = fault_list[i]["Fault"]["Exe_File"]

                                with open(
                                    directory, mode="r", encoding="utf-8"
                                ) as file:
                                    python_file_content = file.read()

                                source_code = fault_list[i]["Fault"]["Source_Code"]
                                mutant_code = fault_list[i]["Fault"]["Mutate_Code"]

                                mutation_process = python_file_content.replace(
                                    source_code, mutant_code
                                )

                                with open(
                                    directory, mode="w", encoding="utf-8"
                                ) as file:
                                    file.write(mutation_process)

                                print("\n\n############")
                                print("Mutant:", str(i))
                                print("#" * 10)

                                try:

                                    status_output = subprocess.Popen(
                                        [
                                            "roslaunch",
                                            folder_name,
                                            ros_exe_file_name,
                                        ]
                                    )
                                    status_output.wait(timeout=60)
                                except subprocess.TimeoutExpired:
                                    status_output.terminate()
                                    survived_counter += 1
                                    print("#" * 10)
                                    print("#      Survived Mutant        #")
                                    print("#" * 10)
                                    print("\n\n")
                                    print("#" * 10)

                                else:
                                    status_output.terminate()
                                    killed_counter += 1
                                    print("#" * 10)
                                    print("#     Killed Mutant           #")
                                    print("#" * 10)
                                    print("\n\n")
                                    print("#" * 10)

                                with open(
                                    directory, mode="w", encoding="utf-8"
                                ) as file:
                                    file.write(python_file_content)

                            print("\n\n############")
                            print("#      Results            #")
                            print("#" * 10)
                            print("\n\n")

                            print("Total Killed Mutant(s):", killed_counter)
                            print("Total Survived Mutant(s):", survived_counter)

                            print(
                                "\nMutation Score:",
                                (killed_counter / (killed_counter + survived_counter))
                                * 100,
                            )

                            print("#" * 10)
                            print("\n\n")

                        else:

                            is_empty_dependent = self.ui.textEdit_40.toPlainText()
                            if is_empty_dependent == "":

                                start_time = time.time()

                                timeout_counter = 0

                                source_code_text = (
                                    self.ui.source_code_content.toPlainText()
                                )

                                fname = "original_code.py"
                                data = source_code_text
                                with open(fname, mode="w", encoding="utf-8") as file:
                                    file.write(data)

                                mutation_list_size = self.ui.listWidget_4.count()
                                time_limit_per_process = (
                                    self.ui.textEdit_18.toPlainText()
                                )

                                subprocess.run("python3 original_code.py", check=True)
                                # cmd = ["python3", "original_code.py"]
                                # try:
                                # 	subprocess.run(cmd, stdout=subprocess.PIPE, shell=True,
                                # timeout=int(time_limit_per_process))
                                # except subprocess.TimeoutExpired:
                                # 	pass

                                print("#" * 10)
                                print("#       Original Code       #")
                                print("#" * 10)

                                # Directory liste içerisinden alınmalı
                                fiplan_directory = self.ui.listWidget_6.item(0).text()
                                with open(
                                    fiplan_directory, encoding="utf-8"
                                ) as json_file:
                                    fault_list = json.load(json_file)

                                # with open("faultPlans.json") as file:
                                #     fault_list = json.load(file)

                                for i in range(0, mutation_list_size):
                                    target_line_from_json = fault_list[i]["Fault"][
                                        "Source_Code"
                                    ]
                                    mutated_code_from_json = fault_list[i]["Fault"][
                                        "Mutate_Code"
                                    ]

                                    main_mutation_process = source_code_text.replace(
                                        target_line_from_json, mutated_code_from_json
                                    )
                                    fname = "fault" + str(i) + ".py"
                                    data = main_mutation_process
                                    with open(
                                        fname, mode="w", encoding="utf-8"
                                    ) as file:
                                        file.write(data)

                                    print("\n\nFault Number: ", i)
                                    print("\n############")

                                    cmd = ["python3", "fault" + str(i) + ".py"]
                                    try:
                                        res = subprocess.run(
                                            cmd,
                                            stdout=subprocess.PIPE,
                                            timeout=int(time_limit_per_process),
                                            check=True,
                                        )
                                    except subprocess.TimeoutExpired:
                                        timeout_counter += 1
                                        execution_timeout_list.append(
                                            "python3 fault" + str(i) + ".py"
                                        )
                                        killed_mutants += 1
                                        killed_mutants_list.append(
                                            "python3 fault" + str(i) + ".py"
                                        )
                                        # error_code_list.append(mutant_code_output)
                                        continue
                                    else:

                                        mutant_code_execution = (
                                            "python3 fault" + str(i) + ".py"
                                        )

                                        subprocess_output_status = (
                                            subprocess.getstatusoutput(
                                                mutant_code_execution
                                            )
                                        )  # Mutant kodları çalıştırıp çıktılarını alır.
                                        mutant_code_output = subprocess_output_status[1]
                                        error_code_list.append(mutant_code_output)

                                        coverage_run_process = (
                                            "coverage run fault" + str(i) + ".py"
                                        )  # Çalıştırılacak "fault"ların isimleri oluşturulur.
                                        coverage_run_process_report = "coverage report"

                                        os.system(
                                            coverage_run_process
                                        )  # Faultlar ayrı ayrı çalıştırılır
                                        os.system(
                                            coverage_run_process_report
                                        )  # Çalıştırılan "fault"un coverage raporunu oluşturur.

                                        if subprocess_output_status[0] != 0:
                                            print(mutant_code_output)
                                            print("#" * 10)
                                            print("#      Killed Mutant         #")
                                            print("#" * 10)
                                            killed_mutants += 1
                                            killed_mutants_list.append(
                                                mutant_code_execution
                                            )
                                            error_code_list.append(mutant_code_output)

                                        else:

                                            if (
                                                mutant_code_output
                                                == original_source_code_output
                                            ):
                                                print(mutant_code_output)
                                                print("#" * 10)
                                                print(
                                                    "#          Equivalent Mutant           #"
                                                )
                                                print("#" * 10)
                                                equivalent_mutants += 1
                                                equivalent_mutants_list.append(
                                                    mutant_code_execution
                                                )

                                            else:
                                                print(mutant_code_output)
                                                print("#" * 10)
                                                print(
                                                    "#       Survivor Mutant          #"
                                                )
                                                print("#" * 10)
                                                survivor_mutants += 1
                                                survived_mutants_list.append(
                                                    mutant_code_execution
                                                )

                                end_time = time.time()

                                print("\n\n")
                                print("#" * 10)
                                print(
                                    "#                     RESULTS                        #"
                                )
                                print("#" * 10)
                                print("\n")

                                print("Process Time: ", end_time - start_time)
                                self.ui.listWidget_9.addItem(
                                    "Process Time:" + str(end_time - start_time)
                                )
                                print("\n")

                                mutation_score = (
                                    killed_mutants / (killed_mutants + survivor_mutants)
                                ) * 100

                                print("Mutation Score: %", mutation_score)
                                self.ui.listWidget_9.addItem(
                                    "Mutation Score: %" + str(mutation_score)
                                )
                                print("\n")
                                print(
                                    "Number of Total Mutants:",
                                    killed_mutants
                                    + survivor_mutants
                                    + equivalent_mutants,
                                )
                                self.ui.listWidget_9.addItem(
                                    "All Mutants: "
                                    + str(
                                        killed_mutants
                                        + survivor_mutants
                                        + equivalent_mutants
                                    )
                                )
                                print("\n")
                                print("Killed Mutants: ", killed_mutants)
                                self.ui.listWidget_9.addItem(
                                    "Killed: " + str(killed_mutants)
                                )
                                print("Survivor Mutants: ", survivor_mutants)
                                self.ui.listWidget_9.addItem(
                                    "Survived: " + str(survivor_mutants)
                                )
                                print("Equivalent Mutants: ", equivalent_mutants)
                                self.ui.listWidget_9.addItem(
                                    "Equivalent: " + str(equivalent_mutants)
                                )
                                print("Timeout: ", timeout_counter)
                                self.ui.listWidget_9.addItem(
                                    "Timeout: " + str(timeout_counter)
                                )

                                print("\n")
                                print("#" * 10)
                                print(
                                    "#                      DETAILS                       #"
                                )
                                print("#" * 10)
                                print("\n")

                                killed_mutant_list_size = len(killed_mutants_list)

                                print("Killed Mutants List: ")
                                self.ui.listWidget_16.addItem("Killed Mutants List: ")
                                for i in range(killed_mutant_list_size):
                                    print(killed_mutants_list[i])
                                    self.ui.listWidget_16.addItem(
                                        str(killed_mutants_list[i])
                                    )

                                print("\n")

                                print("Survivor Mutants List: ")
                                self.ui.listWidget_16.addItem("Survivor Mutants List: ")
                                for i in survived_mutants_list:
                                    print(i)
                                    self.ui.listWidget_16.addItem(str(i))

                                print("\n")

                                print("Equivalent Mutants List: ")
                                self.ui.listWidget_16.addItem(
                                    "Equivalent Mutants List: "
                                )
                                for i in equivalent_mutants_list:
                                    print(i)
                                    self.ui.listWidget_16.addItem(str(i))

                                print("Timeout List: ")
                                self.ui.listWidget_16.addItem("Timeout Mutants List: ")
                                for i in execution_timeout_list:
                                    print(i)
                                    self.ui.listWidget_16.addItem(str(i))

                                print("\n")
                                print("#" * 10)
                                print(
                                    "#             Outputs of Killed Mutants              #"
                                )
                                print("#" * 10)

                                for i in range(killed_mutant_list_size):
                                    print("\n")
                                    print("#" * 10)
                                    print(killed_mutants_list[i])
                                    self.ui.listWidget_19.addItem(
                                        str(killed_mutants_list[i])
                                    )
                                    print(
                                        "" - "*10" - "*10" - "*10" - "*10" - "*10----"
                                    )
                                    error_output = error_code_list[i]
                                    error_output_split = error_output.split("\n")
                                    print(error_output_split[-1])
                                    self.ui.listWidget_19.addItem(
                                        str(error_output_split[-1])
                                    )
                                    print("#" * 10)
                                print("\n")

                                if self.ui.checkBox_7.isChecked() is True:
                                    for i in range(0, mutation_list_size):
                                        path = "fault" + str(i) + ".py"
                                        os.remove(path)

                                    os.remove("original_code.py")
                                    os.remove(".coverage")

                                self.ui.label_10.setText(
                                    "Mutation Score: %" + str(mutation_score)
                                )

                                fault_name_list_size = len(fault_name_list)
                                for i in range(0, fault_name_list_size):
                                    self.ui.listWidget_14.addItem(
                                        "fault"
                                        + str(i)
                                        + ".py --> "
                                        + str(fault_name_list[i])
                                    )
                                    print(str(fault_name_list[i]))

                            else:
                                killed_counter = 0
                                survived_counter = 0

                                fiplan_directory = self.ui.listWidget_6.item(0).text()
                                with open(
                                    fiplan_directory, encoding="utf-8"
                                ) as json_file:
                                    fault_list = json.load(json_file)

                                for i in range(len(fault_list)):
                                    directory = fault_list[i]["Fault"]["File_Directory"]

                                    split_directory = directory.split("/")
                                    folder_name = split_directory[-3]

                                    ros_exe_file_name = fault_list[i]["Fault"][
                                        "Exe_File"
                                    ]

                                    with open(
                                        directory, mode="r", encoding="utf-8"
                                    ) as file:
                                        python_file_content = file.read()

                                    source_code = fault_list[i]["Fault"]["Source_Code"]
                                    mutant_code = fault_list[i]["Fault"]["Mutate_Code"]

                                    print("Source codeeeeeeeeeeeeee:", source_code)
                                    print("Mutant codeeeeeeeeeeeeee:", mutant_code)

                                    mutation_process = python_file_content.replace(
                                        source_code, mutant_code
                                    )

                                    with open(
                                        directory, mode="w", encoding="utf-8"
                                    ) as file:
                                        file.write(mutation_process)

                                    print("\n\n############")
                                    print("Mutant:", (str(i)))
                                    print("#" * 10)

                                    try:
                                        status_output = subprocess.Popen(
                                            [
                                                "roslaunch",
                                                folder_name,
                                                ros_exe_file_name,
                                            ]
                                        )
                                        status_output.wait(timeout=60)
                                    except subprocess.TimeoutExpired:
                                        status_output.terminate()
                                        survived_counter += 1
                                        print("#" * 10)
                                        print("#       Survived Mutant        #")
                                        print("#" * 10)
                                        print("\n\n")
                                        print("#" * 10)

                                    else:
                                        status_output.terminate()
                                        killed_counter += 1
                                        print("#" * 10)
                                        print("#    Killed Mutant            #")
                                        print("#" * 10)
                                        print("\n\n")
                                        print("#" * 10)

                                    with open(
                                        directory, mode="w", encoding="utf-8"
                                    ) as file:
                                        file.write(python_file_content)

                                print("\n\n############")
                                print("#     Results            #")
                                print("#" * 10)
                                print("\n\n")

                                print("Total Killed Mutant(s):", killed_counter)
                                print("Total Survived Mutant(s):", survived_counter)

                                print(
                                    "\nMutation Score:",
                                    (
                                        killed_counter
                                        / (killed_counter + survived_counter)
                                    )
                                    * 100,
                                )

                                print("#" * 10)
                                print("\n\n")

        def metric_info_selection():
            try:
                clicked_item_text = self.ui.listWidget_18.currentItem().text()
                selected_metric = self.ui.listWidget_18.currentItem().text()

                with open("metricList.json", encoding="utf-8") as file:
                    fault_list = json.load(file)

                metric_list_size = self.ui.listWidget_18.count()

                for i in range(0, metric_list_size):
                    metric_name = fault_list["Metrics"][i]["Metric"]["Name"]

                    if clicked_item_text == metric_name:
                        metric_information = fault_list["Metrics"][i]["Metric"]["Info"]
                        self.ui.textEdit_9.setPlainText(metric_information)
            except:
                IndexError()

        def metric_from_list_selection_with_double_click():
            selected_metric = self.ui.listWidget_18.currentItem().text()
            self.ui.listWidget_15.addItem(selected_metric)

        def show_message(message_box_type, message_box_text, message_box_title):
            message_box = QMessageBox()
            if message_box_type == "Critical":
                message_box.setIcon(QMessageBox.Critical)
            if message_box_type == "Ok":
                message_box.setIcon(QMessageBox.Ok)
            if message_box_type == "Critical":
                message_box.setIcon(QMessageBox.Critical)
            message_box.setText(message_box_text)
            message_box.setWindowTitle(message_box_title)
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec()

        # LIST'S (listWidget's) CLICK CONNECTS

        # Line Selection For Mutation on FI Plan Page
        self.ui.listWidget.itemClicked.connect(possible_mutation_line_selection)

        # Line Selection and Show Information About Fault on FI Plan Page
        self.ui.listWidget_3.itemDoubleClicked.connect(fault_selection_from_library)
        self.ui.listWidget_3.itemClicked.connect(show_fault_info_with_one_click)

        # Code Snippet Selection on Start Page
        self.ui.code_snippet_list.itemDoubleClicked.connect(code_snippet_selection)
        self.ui.code_snippet_list.itemClicked.connect(
            code_snippet_select_with_one_clicked
        )

        # Select Task and Show Task's Details on Workload Page
        self.ui.listWidget_21.itemClicked.connect(task_info_with_one_click)
        self.ui.listWidget_21.itemDoubleClicked.connect(task_selection)

        # Select Metric
        self.ui.listWidget_18.itemClicked.connect(metric_info_selection)
        self.ui.listWidget_18.itemDoubleClicked.connect(
            metric_from_list_selection_with_double_click
        )

        # BUTTONS CLICK CONNECTS

        # LEFT MENU BUTTON CONNECTS
        self.ui.btn_home.clicked.connect(self.buttonClick)
        self.ui.btn_start.clicked.connect(self.buttonClick)
        self.ui.btn_scan.clicked.connect(self.buttonClick)
        self.ui.btn_fiplan.clicked.connect(self.buttonClick)
        self.ui.btn_execution.clicked.connect(self.left_menu_execution_page)
        self.ui.btn_monitoring.clicked.connect(self.buttonClick)
        self.ui.open_ros_page.clicked.connect(self.buttonClick)

        # GO TO BUTTON CONNECTS
        self.ui.btn_go_start.clicked.connect(self.go_to_start_page)
        self.ui.btn_go_scan.clicked.connect(self.buttonClick)
        self.ui.btn_go_fiplan.clicked.connect(self.buttonClick)
        self.ui.btn_go_exe.clicked.connect(self.buttonClick)
        self.ui.btn_go_monitoring.clicked.connect(self.buttonClick)
        self.ui.btn_new_one.clicked.connect(self.buttonClick)
        self.ui.back_start_page.clicked.connect(self.buttonClick)
        self.ui.go_execution.clicked.connect(self.buttonClick)

        # START PAGE BUTTON CONNECTS
        self.ui.btn_open_folder.clicked.connect(get_file_py_for_source_code)
        self.ui.btn_select_workload.clicked.connect(workload_get_file_json)
        self.ui.btn_create_workload.clicked.connect(self.buttonClick)
        self.ui.checkBox_5.clicked.connect(self.buttonClick)
        self.ui.btn_clear_codes.clicked.connect(self.buttonClick)
        self.ui.btn_clear_workload.clicked.connect(self.buttonClick)
        self.ui.btn_add_custom.clicked.connect(self.buttonClick)
        self.ui.checkBox_8.clicked.connect(edit_source_code)
        self.ui.checkBox_5.clicked.connect(edit_workload)
        self.ui.btn_open_tc.clicked.connect(get_file_py_for_test_case)
        self.ui.try_test_case.clicked.connect(self.buttonClick)
        self.ui.pushButton_10.clicked.connect(self.buttonClick)

        # CODE SNIPPET BUTTON CONNECTS
        self.ui.btn_create_code.clicked.connect(self.buttonClick)
        self.ui.btn_select_snippet.clicked.connect(code_snippet_selection)
        self.ui.btn_remove_snip.clicked.connect(self.buttonClick)

        # ROS PAGE BUTTON CONNECTS
        self.ui.rosrun_btn.clicked.connect(self.buttonClick)
        self.ui.add_order_btn.clicked.connect(self.buttonClick)
        self.ui.select_trgt_btn.clicked.connect(self.buttonClick)
        self.ui.scan_ros_btn.clicked.connect(self.buttonClick)
        self.ui.mutate_ros_btn.clicked.connect(self.buttonClick)
        self.ui.remove_order_btn.clicked.connect(self.buttonClick)
        self.ui.add_ros_btn.clicked.connect(self.buttonClick)
        self.ui.remove_ros_btn.clicked.connect(self.buttonClick)
        self.ui.remove_ros_mutant.clicked.connect(self.buttonClick)
        self.ui.ros_slct_fiplan.clicked.connect(self.buttonClick)
        self.ui.ros_fiplan_save.clicked.connect(self.buttonClick)
        self.ui.ros_fiplan_remove.clicked.connect(self.buttonClick)
        self.ui.open_target_ros.clicked.connect(self.buttonClick)
        self.ui.ros_test_case.clicked.connect(self.buttonClick)
        self.ui.open_ros_test_case.clicked.connect(self.buttonClick)
        self.ui.ros_try_test_case.clicked.connect(self.buttonClick)
        self.ui.ros_save_test_case.clicked.connect(self.buttonClick)
        self.ui.back_to_start.clicked.connect(self.buttonClick)

        # SCAN PAGE BUTTON CONNECTS
        self.ui.btn_back_code.clicked.connect(self.buttonClick)
        self.ui.btn_scan_process.clicked.connect(self.start_scan_process)

        # FI PLAN PAGE BUTTONS
        self.ui.btn_random_fault.clicked.connect(random_hata_bas)
        self.ui.btn_slct_fiplan.clicked.connect(fiplan_get_file_json)
        self.ui.btn_create_custom.clicked.connect(self.buttonClick)
        self.ui.btn_select_fault.clicked.connect(fault_selection_from_library)
        self.ui.btn_remove_fault.clicked.connect(self.buttonClick)
        self.ui.btn_start_mutation.clicked.connect(basla_func)
        self.ui.btn_save_fiplan.clicked.connect(self.buttonClick)
        self.ui.btn_remove_fiplan.clicked.connect(self.buttonClick)

        # EXECUTION PAGE BUTTONS
        self.ui.btn_new_exe.clicked.connect(self.buttonClick)
        self.ui.btn_remove_exe.clicked.connect(self.buttonClick)
        self.ui.btn_select_metrics.clicked.connect(self.buttonClick)
        self.ui.btn_start_exe.clicked.connect(execution_module_function)

        # MONITORING PAGE BUTTONS
        self.ui.btn_select_scenario.clicked.connect(get_file_rosbag)
        self.ui.btn_run_scenario.clicked.connect(self.buttonClick)
        self.ui.btn_create_report.clicked.connect(self.create_v_and_v_report)

        # CREATE WORKLOAD PAGE BUTTONS
        self.ui.btn_changeDir.clicked.connect(self.buttonClick)
        self.ui.btn_workload_save.clicked.connect(self.buttonClick)
        self.ui.btn_take_tasks.clicked.connect(self.buttonClick)
        self.ui.btn_select_task.clicked.connect(self.buttonClick)
        self.ui.btn_remove_task.clicked.connect(self.buttonClick)
        self.ui.btn_save_task.clicked.connect(self.buttonClick)
        self.ui.btn_back_start.clicked.connect(self.buttonClick)

        # CREATE CUSTOM SNIPPET PAGE BUTTONS
        self.ui.btn_create_snip.clicked.connect(self.buttonClick)
        self.ui.btn_save_snip.clicked.connect(self.buttonClick)
        self.ui.back_snip.clicked.connect(self.buttonClick)
        self.ui.btn_delete_snip.clicked.connect(self.buttonClick)

        # CREATE CUSTOM FAULT PAGE
        self.ui.btn_back_fi.clicked.connect(self.buttonClick)
        self.ui.btn_save_fault.clicked.connect(self.buttonClick)
        self.ui.btn_create_fault.clicked.connect(self.buttonClick)
        self.ui.btn_delete_fault.clicked.connect(self.buttonClick)
        self.ui.btn_remove_createdFault.clicked.connect(self.buttonClick)

        # METRICS PAGE BUTTONS
        self.ui.btn_metric_list.clicked.connect(
            metric_from_list_selection_with_double_click
        )
        self.ui.saveMetrics.clicked.connect(self.buttonClick)
        self.ui.btn_back_exe.clicked.connect(self.buttonClick)

        # SHOW APP
        self.show()

        # SET CUSTOM THEME
        use_custom_theme = False

        # SET HOME PAGE AND SELECT MENU
        self.ui.stackedWidget.setCurrentWidget(self.ui.home)
        self.ui.btn_home.setStyleSheet(
            UIFunctions.selectMenu(self.ui.btn_home.styleSheet())
        )

    def left_menu_execution_page(self):
        """Go to execution page from left menu"""
        self.ui.stackedWidget.setCurrentWidget(self.ui.execution)
        UIFunctions.resetStyle(self, self.ui.btn_execution)
        self.sender().setStyleSheet(UIFunctions.selectMenu(self.sender().styleSheet()))
        self.ui.titleRightInfo.setText("EXECUTION")

    def go_to_start_page(self):
        """GO to start page button"""
        # connection = dbConnection.connect("VVToolDataBase","postgres","root")
        # connection.commit()

        self.ui.stackedWidget.setCurrentWidget(self.ui.start)
        UIFunctions.resetStyle(self, self.ui.btn_home.styleSheet())
        self.ui.btn_start.setStyleSheet(
            UIFunctions.selectMenu(self.ui.btn_start.styleSheet())
        )
        self.ui.titleRightInfo.setText("START")

        name = "Source Code Example"
        description = "Settings Example"

        # db_connection_status = False

        # if db_connection_status is True:
        #     IMFIT_functions.insert_system(connection, name, description)

    # Splits source code to scan line by line
    def take_split_source_code(self):
        """The function provides the splitted code to scan line by line"""
        pure_source_code_content = self.ui.textEdit_4.toPlainText()
        split_text = pure_source_code_content.split("\n")
        self.ui.listWidget_2.addItems(split_text)

        return split_text

    # Scan Process Main Function
    def start_scan_process(self):
        """The function decides which scan process path to use"""
        check_detected_parts_list = self.ui.listWidget_2.count()

        # self.ui.listWidget_2.add
        if check_detected_parts_list:
            self.ui.listWidget_2.clear()

        scan_page_source_code_check = self.ui.textEdit_4.toPlainText()

        if scan_page_source_code_check:
            is_empty_workload = len(self.ui.textEdit_22.toPlainText())
            selected_code_snippet_length = self.ui.listWidget_17.count()

            if is_empty_workload == 0 and selected_code_snippet_length == 0:
                self.start_no_workload_no_code_snippet_process()
            elif is_empty_workload > 0 and selected_code_snippet_length == 0:
                self.start_yes_workload_no_code_snippet_process()
            elif is_empty_workload == 0 and selected_code_snippet_length > 0:
                self.start_no_workload_yes_code_snippet_process()
            else:
                self.start_yes_workload_yes_code_snippet_process()

    # Function starts "Yes Workload, Yes Code Snipet" Scan Process
    def start_yes_workload_yes_code_snippet_process(self):
        """Function manages yes workload, yes code snippet scan process"""
        detected_part_list_size = self.ui.listWidget_2.count()
        selected_code_snippet_length = self.ui.listWidget_17.count()
        code_snippet_regex_code = scan_process.open_code_snip()
        workload_text = self.ui.textEdit_22.toPlainText()
        workload_data = json.loads(workload_text)
        workload_function_name_list = scan_process.take_workload_name_list(
            workload_data
        )
        split_text = self.take_split_source_code()
        painted_lines = scan_process.workload_lines(
            split_text, workload_function_name_list
        )
        (
            added_snippet_regex_length,
            code_snippet_data_list,
        ) = self.find_selected_code_snippet(
            selected_code_snippet_length, code_snippet_regex_code
        )
        patterns = scan_process.find_patterns_yes_wl_yes_cs(
            added_snippet_regex_length, code_snippet_data_list
        )
        source_code_list = self.take_source_code()
        (
            faultable_line_list,
            faultable_line_number_list,
        ) = scan_process.scan_yes_wl_yes_cs(patterns, source_code_list, painted_lines)

        self.scan_process_progress_bar()
        self.paint_workload_lines(painted_lines)
        self.paint_sky_blue(faultable_line_number_list)
        self.add_fi_plan(faultable_line_list)

    # Progress bar on scan page
    def scan_process_progress_bar(self):
        """Progress Bar"""
        for i in range(100):
            time.sleep(0.01)
            self.ui.progressBar_2.setValue(i + 1)

    # Function takes source code to use on IM-FIT
    def take_source_code(self):
        """Take Source Code from UI"""
        source_code_list = []
        source_code = self.ui.textEdit_4.toPlainText()
        source_code_list = source_code.split("\n")

        return source_code_list

    # Function paints workload covered and
    # selected code snippets lines to show to the user on UI
    def paint_sky_blue(self, faultable_line_number_list):
        """In "Yes Workload, Yes Workload" Process,
        this function paints the detected parts of code as sky blue"""
        for i in faultable_line_number_list:
            self.ui.listWidget_2.item(i).setBackground(
                QtGui.QColor(0, 128, 255)
            )  # Colored as sky blue

    # Function paints workload covered lines to show to the user on UI
    def paint_workload_lines(self, painted_lines):
        """In "Yes Workload, Yes Workload" Process,
        this function paints the detected parts of workload as purple"""
        for number in painted_lines:
            self.ui.listWidget_2.item(number).setBackground(
                QtGui.QColor(102, 0, 102)
            )  # Colored as purple

    # Function finds selected code snippets by the user in source code
    def find_selected_code_snippet(
        self, selected_code_snippet_length, code_snippet_regex_code
    ):
        """Selected code snippets by the user are finded by IM-FIT"""
        code_snippet_data_list = []
        for i in range(selected_code_snippet_length):
            code_snippet_data = self.ui.listWidget_17.item(i).text()
            code_snippet_data_list.append(code_snippet_data)
            added_snippet_regex_length = len(code_snippet_regex_code["code_snippets"])
        return added_snippet_regex_length, code_snippet_data_list

    # Function adds the faultable lines to FI Plan page
    def add_fi_plan(self, faultable_line_list):
        """Detected fault applicable lines
        add to FI Plan page to apply mutation testing"""
        for painted_line in faultable_line_list:
            strip_painted_line = painted_line.strip()
            self.ui.listWidget.addItem(strip_painted_line)

    # Function starts "No Workload, No Code Snipet" Scan Process
    def start_no_workload_no_code_snippet_process(self):
        """Function manages no workload, no code snippet scan process"""
        code_snippet_regex_code_list = scan_process.take_code_snippet_regex_code_list()
        source_code_list = self.take_source_code()
        (
            faultable_line_number_list,
            faultable_line_list,
        ) = scan_process.no_wl_no_cs_find_target_line(
            source_code_list, code_snippet_regex_code_list
        )
        self.take_split_source_code()
        self.scan_process_progress_bar()
        self.paint_sky_blue(faultable_line_number_list)
        self.add_fi_plan(faultable_line_list)

    # Function starts "Yes Workload, No Code Snippet" Scan Process
    def start_yes_workload_no_code_snippet_process(self):
        """Function manages yes workload, no code snippet scan process"""
        split_text = self.take_split_source_code()
        workload_text = self.ui.textEdit_22.toPlainText()
        workload_data = json.loads(workload_text)
        workload_function_name_list = scan_process.take_workload_name_list(
            workload_data
        )
        painted_lines = scan_process.workload_lines(
            split_text, workload_function_name_list
        )
        patterns = scan_process.take_code_snippet_regex_code_list()
        (
            faultable_line_list,
            faultable_line_number_list,
        ) = scan_process.yes_workload_no_snippet_target_line(
            patterns, painted_lines, split_text
        )
        self.scan_process_progress_bar()
        self.paint_workload_lines(painted_lines)
        self.paint_sky_blue(faultable_line_number_list)
        self.add_fi_plan(faultable_line_list)

    # Method takes code snippet for "No Workload, Yes Code Snippet" Scan Process
    def take_code_snippet_no_workload_yes_code_snippet(self):
        """Code snippets are taken by IM-FIT to use on no workload yes code snippet scan process"""
        selected_code_snippet_length = self.ui.listWidget_17.count()
        code_snippet_data_list = []
        for line_number in range(selected_code_snippet_length):
            line_from_code_snippet_list = self.ui.listWidget_17.item(line_number).text()
            code_snippet_data_list.append(line_from_code_snippet_list)
        return code_snippet_data_list

    # Method start "No Workload, Yes Code Snippet" Scan Process
    def start_no_workload_yes_code_snippet_process(self):
        """Method manages no workload yes code snippet scan process"""
        detected_part_list_size = self.ui.listWidget_2.count()
        code_snippet_data_list = self.take_code_snippet_no_workload_yes_code_snippet()
        patterns = scan_process.define_code_snippet_no_workload_yes_code_snippet(
            code_snippet_data_list
        )
        split_text = self.take_split_source_code()
        (
            faultable_line_list,
            faultable_line_number_list,
        ) = scan_process.find_target_no_workload_yes_code_snippet(split_text, patterns)
        self.scan_process_progress_bar()
        self.paint_sky_blue(faultable_line_number_list)
        self.add_fi_plan(faultable_line_list)

    # # Method creates V&V report to show details of the mutation process to the user
    # def create_v_and_v_report(self):
    #     """ v&v Report is created by IM-FIT with using this method """
    #     # save FPDF() class into a
    #     # variable pdf
    #     pdf = FPDF()

    #     # Add a page
    #     pdf.add_page()

    #     # set style and size of font
    #     # that you want in the pdf
    #     pdf.set_font("Arial", size=9)

    #     v_and_v_report_introduction = """
    #     The V&V Report Created by IM-FIT
    #     This reports shows information about AST Diagram of Source Codes, Fault List, Metric List, Rosbag Scenarios, etc.
    #     Therefore the user can learn about its source codes.

    #     IM-FIT
    #     """
    #     pdf.cell(200, 10, txt=v_and_v_report_introduction, ln=1, align="C")

    #     monitoring_ast_diagram = self.ui.textEdit_23.toPlainText()
    #     pdf.cell(200, 10, txt=monitoring_ast_diagram, ln=1, align="L")

    #     monitoring_metric_list_size = self.ui.listWidget_9.count()
    #     for i in range(0, monitoring_metric_list_size):
    #         # create a cell
    #         line_of_metric_list = self.ui.listWidget_9.item(i).text()
    #         pdf.cell(200, 10, txt=line_of_metric_list, ln=2, align="L")

    #     monitoring_mutant_list_size = self.ui.listWidget_16.count()
    #     for i in range(0, monitoring_mutant_list_size):
    #         # create a cell
    #         line_of_mutant_list = self.ui.listWidget_16.item(i).text()
    #         pdf.cell(200, 10, txt=line_of_mutant_list, ln=3, align="L")

    #     monitoring_killed_mutants_output_list_size = self.ui.listWidget_19.count()
    #     for i in range(0, monitoring_killed_mutants_output_list_size):
    #         # create a cell
    #         line_of_killed_mutants_output_list = self.ui.listWidget_19.item(i).text()
    #         pdf.cell(200, 10, txt=line_of_killed_mutants_output_list, ln=4, align="L")

    #     monitoring_faults_list_size = self.ui.listWidget_14.count()
    #     for i in range(0, monitoring_faults_list_size):
    #         # create a cell
    #         line_of_faults_list = self.ui.listWidget_14.item(i).text()
    #         pdf.cell(200, 10, txt=line_of_faults_list, ln=5, align="L")

    #     monitoring_rosbag_scenarios_list_size = self.ui.listWidget_12.count()
    #     for i in range(0, monitoring_rosbag_scenarios_list_size):
    #         # create a cell
    #         line_of_rosbag_scenarios_list = self.ui.listWidget_12.item(i).text()
    #         pdf.cell(200, 10, txt=line_of_rosbag_scenarios_list, ln=6, align="L")

    #     # # save the pdf with name .pdf
    #     pdf.output("V&V_Report_by_IM-FIT.pdf")
    #     self.ui.label_77.setText("V&V Report is Created")

    def monitoring_report_rosbag_scenarios_list(self):
        """Method adds rosbag scenarios to the rosbag scenarios list on monitoring page"""
        monitoring_rosbag_scenarios_list = []
        monitoring_rosbag_scenarios_list_size = self.ui.listWidget_12.count()
        for i in range(0, monitoring_rosbag_scenarios_list_size):
            line_of_rosbag_scenarios_list_line = self.ui.listWidget_12.item(i).text()
            monitoring_rosbag_scenarios_list.append(line_of_rosbag_scanarios_list_line)
        return monitoring_rosbag_scenarios_list

    def monitoring_report_faults_list(self):
        """Method shows the detected faults after execution process in fault list on monitoring page"""
        monitoring_faults_list = []
        monitoring_faults_list_size = self.ui.listWidget_14.count()
        for i in range(0, monitoring_faults_list_size):
            line_of_faults_list = self.ui.listWidget_14.item(i).text()
            monitoring_faults_list.append(line_of_faults_list)
        return monitoring_faults_list

    def monitoring_report_killed_mutants_output_list(self):
        """Outputs of detected killed mutants are added to the killed mutants output list by IM-FIT on monitoring page"""
        monitoring_killed_mutants_output_list = []
        monitoring_killed_mutants_output_list_size = self.ui.listWidget_19.count()
        for i in range(0, monitoring_killed_mutants_output_list_size):
            line_of_killed_mutants_output_list = self.ui.listWidget_19.item(i).text()
            monitoring_killed_mutants_output_list.append(
                line_of_killed_mutants_output_list
            )
        return monitoring_killed_mutants_output_list

    def monitoring_report_mutant_list(self):
        """Detected mutants are shown to the user by IM-FIT on monitoring page"""
        monitoring_mutant_list = []
        monitoring_mutant_list_size = self.ui.listWidget_16.count()
        for i in range(0, monitoring_mutant_list_size):
            line_of_mutant_list = self.ui.listWidget_16.item(i).text()
            monitoring_mutant_list.append(line_of_mutant_list)
        return monitroing_mutant_list

    def monitoring_report_metric_list(self):
        """Used metrics for the execution process and their results are shown to the user in the list on monitoring page"""
        monitoring_metric_list = []
        monitoring_metric_list_size = self.ui.listWidget_9.count()
        for i in range(0, monitoring_metric_list_size):
            line_of_metric_list = self.ui.listWidget_9.item(i).text()
            monitoring_metric_list.append(line_of_metric_list)
        return monitoring_metric_list

    def create_v_and_v_report(self):
        """Method manages creating a V&V report"""
        monitoring_metric_list = self.monitoring_report_metric_list()
        monitroing_mutant_list = self.monitoring_report_mutant_list()
        monitoring_killed_mutants_output_list = (
            self.monitoring_report_killed_mutants_output_list()
        )
        monitoring_faults_list = self.monitoring_report_faults_list()
        monitoring_rosbag_scenarios_list = (
            self.monitoring_report_rosbag_scenarios_list()
        )
        monitoring_process.create_new_v_and_v_report(
            monitoring_metric_list,
            monitroing_mutant_list,
            monitoring_killed_mutants_output_list,
            monitoring_faults_list,
            monitoring_rosbag_scenarios_list,
        )
        self.ui.label_77.setText("V&V Report is Created")

    # BUTTONS CLICK FUNCTIONS

    def buttonClick(self):
        """Button click function"""
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # HOME PAGE
        if btnName == "btn_home":
            self.ui.stackedWidget.setCurrentWidget(self.ui.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.ui.titleRightInfo.setText("HOME")

        # START PAGE
        if btnName == "btn_start":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.ui.titleRightInfo.setText("START")

        # SCAN PAGE
        if btnName == "btn_scan":
            self.ui.stackedWidget.setCurrentWidget(self.ui.scan)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.ui.titleRightInfo.setText("SCAN")

        # CODE SNIPPETS PAGE
        if btnName == "btn_code":
            self.ui.stackedWidget.setCurrentWidget(self.ui.code)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.ui.titleRightInfo.setText("CODE SNIPPETS")

        # FIPLAN PAGE
        if btnName == "btn_fiplan":
            self.ui.stackedWidget.setCurrentWidget(self.ui.fiplan)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.ui.titleRightInfo.setText("FAULT INJECTION PLAN")

        # EXECUTION PAGE
        if btnName == "btn_execution":
            self.ui.stackedWidget.setCurrentWidget(self.ui.execution)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.ui.titleRightInfo.setText("EXECUTION")

        # MONITORING PAGE
        if btnName == "btn_monitoring":
            self.ui.stackedWidget.setCurrentWidget(self.ui.monitoring)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))
            self.ui.titleRightInfo.setText("MONITORING")

        ### PAGE CHANGE BUTTONS ###

        if btnName == "btn_go_start":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            UIFunctions.resetStyle(self, self.ui.btn_home.styleSheet())
            self.ui.btn_start.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_start.styleSheet())
            )
            self.ui.titleRightInfo.setText("START")

        if btnName == "btn_go_start_2":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            UIFunctions.resetStyle(self, self.ui.btn_home.styleSheet())
            self.ui.btn_start.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_start.styleSheet())
            )
            self.ui.titleRightInfo.setText("START")

        if btnName == "back_start_page":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            self.ui.titleRightInfo.setText("START")

        if btnName == "btn_go_scan":
            self.ui.stackedWidget.setCurrentWidget(self.ui.scan)
            UIFunctions.resetStyle(self, self.ui.btn_start.styleSheet())
            self.ui.btn_scan.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_scan.styleSheet())
            )
            self.ui.titleRightInfo.setText("SCAN")
            # self.ui.textEdit_3.clear()

            # check_source_code_text = self.ui.textEdit_4.toPlainText()
            # check_workload_text = self.ui.textEdit_22.toPlainText()
            # check_code_snippet_list = self.ui.listWidget_17.count()

            # if check_source_code_text or check_workload_text or check_code_snippet_list:
            #     self.ui.textEdit_4.clear()
            #     self.ui.textEdit_22.clear()
            #     self.ui.listWidget_17.clear()

            if self.ui.checkBox_3.isChecked() is True:
                self.ui.textEdit_4.setPlainText(
                    self.ui.source_code_content.toPlainText()
                )
                self.ui.textEdit_22.setPlainText(self.ui.textEdit_3.toPlainText())
                check_selected_code_snippet_list = self.ui.listWidget_8.count()

                if check_selected_code_snippet_list:
                    code_snippet_data_list = []
                    for i in range(0, check_selected_code_snippet_list):
                        code_snippet_data = self.ui.listWidget_8.item(i).text()
                        code_snippet_data_list.append(code_snippet_data)

                    self.ui.listWidget_17.addItems(code_snippet_data_list)

        if btnName == "btn_go_fiplan":
            self.ui.stackedWidget.setCurrentWidget(self.ui.fiplan)
            UIFunctions.resetStyle(self, self.ui.btn_scan.styleSheet())
            self.ui.btn_fiplan.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_fiplan.styleSheet())
            )
            self.ui.titleRightInfo.setText("FAULT INJECTION PLAN")

            for original_line in self.code_part_for_mutation:
                if not isinstance(original_line, int):
                    new_line = original_line.lstrip()
                    self.ui.listWidget.addItem(new_line)

            line_number = self.ui.listWidget.count()

            for number in range(0, line_number):
                if number % 2 == 0:
                    self.ui.listWidget.item(number).setBackground(
                        QtGui.QColor(52, 59, 72)
                    )  # Gri
                else:
                    self.ui.listWidget.item(number).setBackground(
                        QtGui.QColor(40, 44, 52)
                    )  # Arka plan rengi

        if btnName == "btn_go_exe":
            self.ui.stackedWidget.setCurrentWidget(self.ui.execution)
            UIFunctions.resetStyle(self, self.ui.btn_fiplan.styleSheet())
            self.ui.btn_execution.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_execution.styleSheet())
            )
            self.ui.titleRightInfo.setText("EXECUTION")

        if btnName == "btn_go_exe_2":
            self.ui.stackedWidget.setCurrentWidget(self.ui.execution)
            UIFunctions.resetStyle(self, self.ui.btn_fiplan.styleSheet())
            self.ui.btn_execution.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_execution.styleSheet())
            )
            self.ui.titleRightInfo.setText("EXECUTION")

        if btnName == "go_execution":
            self.ui.stackedWidget.setCurrentWidget(self.ui.execution)
            UIFunctions.resetStyle(self, self.ui.btn_start.styleSheet())
            self.ui.btn_execution.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_execution.styleSheet())
            )
            self.ui.titleRightInfo.setText("EXECUTION")

        if btnName == "btn_go_monitoring":
            self.ui.stackedWidget.setCurrentWidget(self.ui.monitoring)
            UIFunctions.resetStyle(self, self.ui.btn_execution.styleSheet())
            self.ui.btn_monitoring.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_monitoring.styleSheet())
            )
            self.ui.titleRightInfo.setText("MONITORING")

        if btnName == "btn_new_one":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            UIFunctions.resetStyle(self, self.ui.btn_monitoring.styleSheet())
            self.ui.btn_start.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_start.styleSheet())
            )
            self.ui.titleRightInfo.setText("START")

        ### PAGES ###

        # START PAGE

        if btnName == "open_ros_page":
            self.ui.stackedWidget.setCurrentWidget(self.ui.ros_page)
            self.ui.titleRightInfo.setText("ROS Mutation Module")
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "btn_create_workload":
            self.ui.stackedWidget.setCurrentWidget(self.ui.cWorkload)
            self.ui.leftMenuBg.hide()
            self.ui.toggleButton.show()
            self.ui.titleRightInfo.setText("START - CREATE WORKLOAD")

        if btnName == "btn_add_custom":
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.json"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()

                if file_name[0].endswith(".json"):
                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()
                        self.ui.textEdit_24.setPlainText(data)
                        code_snippets_list_json = json.loads(data)

                        task_name = str(code_snippets_list_json["Snippet_Name"])
                        self.ui.listWidget_8.addItem(task_name)
                        self.ui.code_snippet_list.addItem(task_name)

        if btnName == "btn_clear_codes":
            self.ui.source_code_content.clear()

        if btnName == "btn_clear_workload":
            self.ui.textEdit_3.clear()

        if btnName == "try_test_case":
            test_code_for_test_case = (
                "import pytest\n"
                + self.ui.source_code_content.toPlainText()
                + "\n"
                + self.ui.test_case_content.toPlainText()
            )
            with open("test_code.py", mode="w+", encoding="utf-8") as file:
                file.write(test_code_for_test_case)

            output = subprocess.getstatusoutput("pytest test_code.py")
            new_output = re.sub("=", "", output[1])

            self.ui.test_case_terminal.setPlainText(new_output)

        if btnName == "pushButton_10":

            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("*.py *.launch")

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                if file_name[0].endswith(".py") or file_name[0].endswith(".launch"):

                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()
                        self.ui.textEdit_21.setPlainText(file_name[0])
                        self.ui.textEdit_40.setPlainText(data)
                else:
                    message_box = QMessageBox()
                    message_box.setIcon(QMessageBox.Critical)
                    message_box.setText(
                        "Please be sure to selected .py or .launch file!"
                    )
                    message_box.setWindowTitle("Attention!")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()

        # CREATE WORKLOAD PAGE FROM START PAGE

        if btnName == "btn_changeDir":
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.json"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                if file_name[0].endswith(".json"):  # .json file is choosed by the user
                    with open(
                        file_name[0], mode="r", encoding="utf-8"
                    ) as file:  # file_name[0] is directory of file
                        workload_content_data = file.read()
                        self.ui.textEdit_44.setPlainText(
                            str(file_name[0])
                        )  # Source code directory is added to the text
                        self.ui.plainTextEdit.setPlainText(workload_content_data)
                        self.ui.plainTextEdit_2.setPlainText(workload_content_data)

        if btnName == "btn_workload_save":
            dialog = QFileDialog()
            path_name = QFileDialog.getExistingDirectory()
            text = self.ui.textEdit_42.toPlainText() + ".json"
            full_path = os.path.join(path_name, text)
            created_workload_content = self.ui.plainTextEdit_2.toPlainText()

            with open(full_path, mode="w", encoding="utf-8") as file:
                file.write(created_workload_content)

        if btnName == "btn_take_tasks":
            try:
                all_task_list_size = self.ui.listWidget_21.count()
                json_type_task = self.ui.plainTextEdit.toPlainText()
                json_loaded_task = json.loads(json_type_task)

                if all_task_list_size == 0:

                    for i in range(0, len(json_loaded_task["Tasks"])):
                        workload_task = str(
                            json_loaded_task["Tasks"][i]["Task"]["Task_ID"]
                        )
                        split_workload_task = workload_task.split("\n")
                        self.ui.listWidget_21.addItems(split_workload_task)
                else:
                    self.ui.listWidget_21.clear()

                    for i in range(0, len(json_loaded_task["Tasks"])):
                        workload_task = str(
                            json_loaded_task["Tasks"][i]["Task"]["Task_ID"]
                        )
                        split_workload_task = workload_task.split("\n")
                        self.ui.listWidget_21.addItems(split_workload_task)
            except:
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Critical)
                caution_text = """Please Fix Workload!
                This is the example workload template.
                
                "Task":{
                    "Task_ID": DATA,
                    "Tag": DATA TAG,
                    "Process": DATA PROCESS,
                    "Sayilar": {
                        "Sayi1":XX,
                        "Sayi2":XX
                    }
                }"""
                message_box.setText(caution_text)
                message_box.setWindowTitle("Fix Workload!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

        if btnName == "btn_select_task":
            selected_task_from_list = self.ui.listWidget_21.currentItem().text()
            split_selected_task_from_list = selected_task_from_list.split("\n")
            self.ui.listWidget_22.addItems(split_selected_task_from_list)

        if btnName == "btn_save_task":
            all_selected_snippets = ""

            selected_task_list_size = self.ui.listWidget_22.count()

            json_type_task = self.ui.plainTextEdit.toPlainText()
            tasks_list_json = json.loads(json_type_task)

            if selected_task_list_size:
                dialog = QFileDialog()
                path_name = QFileDialog.getExistingDirectory()

                task_name = self.ui.textEdit_5.toPlainText()

                task_path_and_name = os.path.join(path_name, task_name + ".json")

                for i in range(0, len(tasks_list_json["Tasks"])):
                    task_name = str(tasks_list_json["Tasks"][i]["Task"]["Task_ID"])
                    for j in range(0, self.ui.listWidget_22.count()):
                        list_item = self.ui.listWidget_22.item(j).text()
                        if task_name == list_item:
                            task_detail = str(tasks_list_json["Tasks"][i]["Task"])
                            for i in task_detail:
                                all_selected_snippets += i

                with open(task_path_and_name, mode="w", encoding="utf-8") as json_file:
                    json_file.write(all_selected_snippets)

                self.ui.label_4.setText("SAVED!")

        if btnName == "btn_remove_task":
            row = self.ui.listWidget_22.currentRow()
            self.ui.listWidget_22.takeItem(row)

        if btnName == "btn_back_start":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            self.ui.leftMenuBg.show()
            self.ui.titleRightInfo.setText("START")

        # ROS PAGE at START PAGE

        if btnName == "ros_fiplan_save":
            if self.ui.textEdit_45.toPlainText() != "":
                global ROS_SOURCE_MUTANT
                ROS_SOURCE_MUTANT = []

                global fi_plan_directory_list

                mut_list = []

                dialog = QFileDialog()
                path_name = QFileDialog.getExistingDirectory()

                directory = self.ui.textEdit_47.toPlainText()

                split_directory = directory.split("/")

                if path_name != "":
                    if split_directory[-2] == "launch":
                        ros_fiplan_name = (
                            self.ui.textEdit_45.toPlainText() + "_type_launch.json"
                        )
                    else:
                        ros_fiplan_name = (
                            self.ui.textEdit_45.toPlainText() + "_type_rospy.json"
                        )

                    len_ros_source_mutant = len(ROS_SOURCE_MUTANT)

                    for i in range(0, len_ros_source_mutant):

                        if i % 3 == 0:
                            file_directory = ROS_SOURCE_MUTANT[i]
                            original_code = ROS_SOURCE_MUTANT[i + 1]
                            mutant_code = ROS_SOURCE_MUTANT[i + 2]
                            if original_code != mutant_code:
                                created_fault = {
                                    "Fault": {
                                        "File_Directory": file_directory,
                                        "Source_Code": original_code,
                                        "Mutate_Code": mutant_code,
                                        "Exe_File:": self.ui.label_86.text(),
                                    }
                                }

                                mut_list.append(created_fault)

                                # with open("faultPlans", "r+") as file:
                                #     file_data = json.load(file)
                                #     file_data["fault_plans"].append(created_fault)
                                #     file.seek(0)
                                #     json.dump(file_data, file, indent=4)

                                def write_json(new_data, filename):
                                    desired_dir = path_name
                                    full_path = os.path.join(
                                        desired_dir, ros_fiplan_name
                                    )
                                    with open(
                                        full_path, mode="w", encoding="utf-8"
                                    ) as file:
                                        # file_data["fault_plans"].append(created_fault)
                                        # file.seek(0)
                                        json_string = json.dumps(new_data, indent=4)
                                        file.write(json_string)
                                    return full_path

                    ros_fi_plan_path = write_json(mut_list, ros_fiplan_name)
                    # ROS FI Plan Name and Directory Path added to the list
                    fi_plan_directory_list.append(ros_fi_plan_path)

                    split_text = str(fi_plan_directory_list[-1]).split("\n")
                    self.ui.listWidget_36.addItems(split_text)
                    self.ui.listWidget_6.addItems(split_text)

                else:
                    message_box = QMessageBox()
                    message_box.setIcon(QMessageBox.Critical)
                    message_box.setText("Select Directory to Save FI Plan")
                    message_box.setWindowTitle("Warning!")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()

            else:
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Critical)
                message_box.setText("Check Mutant Codes and FI Plan Name")
                message_box.setWindowTitle("Caution!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

        if btnName == "rosrun_btn":

            def rospy_run():
                """main func"""
                global RUN_ORDER_LIST_JUST_PATH
                RUN_ORDER_LIST_JUST_PATH = []
                global ros_process

                len_run_order_list_just_path = len(RUN_ORDER_LIST_JUST_PATH)
                roscore_process = subprocess.Popen(["roscore"])
                time.sleep(5)

                message_box.setIcon(QMessageBox.Information)
                message_box.setText("Roscore is ready!")
                message_box.setWindowTitle("Ready!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

                for i in range(len_run_order_list_just_path):
                    if i % 2 == 0:
                        ros_directory = RUN_ORDER_LIST_JUST_PATH[i]
                        split_rospy_file_name = ros_directory.split("/")
                        package_name = split_rospy_file_name[-3]

                    else:
                        rospy_file_name = RUN_ORDER_LIST_JUST_PATH[i]
                        if i == 1:
                            target_ros_process = subprocess.Popen(
                                ["rosrun", package_name, rospy_file_name]
                            )
                        else:
                            ros_subprocess = subprocess.Popen(
                                ["rosrun", package_name, rospy_file_name]
                            )
                            try:
                                print("Running in process", target_ros_process.pid)
                                target_ros_process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                rosnode_list = subprocess.getoutput("rosnode list")
                                rostopic_list = subprocess.getoutput("rostopic list")
                                rosparam_list = subprocess.getoutput("rosparam list")
                                rosservice_list = subprocess.getoutput(
                                    "rosservice list"
                                )
                                # rosmsg_list = subprocess.getoutput('rosmsg list')
                                # rossrv_list = subprocess.getoutput('rossrv list')
                                print("Timed out - killing", target_ros_process.pid)
                                target_ros_process.terminate()
                                ros_subprocess.terminate()
                                roscore_process.terminate()

                time.sleep(1)
                print("Process Done")

                rosnodes = rosnode_list.split("\n")
                self.ui.listWidget_27.addItems(rosnodes)

                # ROS TOPIC LIST
                rostopics = rostopic_list.split("\n")
                self.ui.listWidget_28.addItems(rostopics)

                # ROS SERVICE LIST
                rosservices = rosservice_list.split("\n")
                self.ui.listWidget_29.addItems(rosservices)

                # ROS PARAMETER LIST
                rosparams = rosparam_list.split("\n")
                self.ui.listWidget_30.addItems(rosparams)

                # # ROS MESSAGE LIST
                # print(rosmsg_list)
                # # ROS SRV LIST
                # print(rossrv_list)

            def launch_run():
                """main func"""

                roscore_process = subprocess.Popen(["roscore"])
                time.sleep(5)

                message_box.setIcon(QMessageBox.Information)
                message_box.setText("Roscore is ready!")
                message_box.setWindowTitle("Ready!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

                roslaunch_folder_directory_path = self.ui.textEdit_47.toPlainText()
                split_roslaunch_folder_directory_path = (
                    roslaunch_folder_directory_path.split("/")
                )

                folder_name = split_roslaunch_folder_directory_path[-3]
                print(folder_name)

                ros_exe_file_name = self.ui.label_86.text()

                ros_process = subprocess.Popen(
                    [
                        "roslaunch",
                        folder_name,
                        ros_exe_file_name,
                    ]
                )
                try:
                    print("Running in process", ros_process.pid)
                    ros_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    rosnode_list = subprocess.getoutput("rosnode list")
                    rostopic_list = subprocess.getoutput("rostopic list")
                    rosparam_list = subprocess.getoutput("rosparam list")
                    rosservice_list = subprocess.getoutput("rosservice list")
                    # rosmsg_list = subprocess.getoutput('rosmsg list')
                    # rossrv_list = subprocess.getoutput('rossrv list')
                    print("Timed out - killing", ros_process.pid)
                    ros_process.terminate()
                    roscore_process.terminate()

                time.sleep(1)
                print("Process Done")

                rosnodes = rosnode_list.split("\n")
                self.ui.listWidget_27.addItems(rosnodes)

                # ROS TOPIC LIST
                rostopics = rostopic_list.split("\n")
                self.ui.listWidget_28.addItems(rostopics)

                # ROS SERVICE LIST
                rosservices = rosservice_list.split("\n")
                self.ui.listWidget_29.addItems(rosservices)

                # ROS PARAMETER LIST
                rosparams = rosparam_list.split("\n")
                self.ui.listWidget_30.addItems(rosparams)

                # # ROS MESSAGE LIST
                # print(rosmsg_list)
                # # ROS SRV LIST
                # print(rossrv_list)

            directory = self.ui.textEdit_47.toPlainText()
            split_directory = directory.split("/")

            if split_directory[-2] == "launch":
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Information)
                message_box.setText("Process Started. Please Wait!")
                message_box.setWindowTitle("Started!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()
                launch_run()
                message_box.setIcon(QMessageBox.Information)
                message_box.setText("Process Done")
                message_box.setWindowTitle("Done!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

            elif split_directory[-2] == "scripts" or split_directory[-2] == "src":
                if self.ui.checkBox_11.isChecked() is True:
                    message_box = QMessageBox()
                    message_box.setIcon(QMessageBox.Information)
                    message_box.setText("Process Started. Please Wait!")
                    message_box.setWindowTitle("Started!")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()
                    rospy_run()
                    message_box.setIcon(QMessageBox.Information)
                    message_box.setText("Process Done")
                    message_box.setWindowTitle("Done!")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()
                else:
                    message_box = QMessageBox()
                    message_box.setIcon(QMessageBox.Warning)
                    message_box.setText("Be sure to select launch or scripts/src file!")
                    message_box.setWindowTitle("Attention")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()
            else:
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Warning)
                message_box.setText("Be sure to select launch or scripts/src file!")
                message_box.setWindowTitle("Attention")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

        if btnName == "add_order_btn":
            # ROS Package
            target_file_path = self.ui.textEdit_47.toPlainText()
            splitted_target_path = target_file_path.split("/")

            try:
                file_from_tree = str(self.ui.treeView.selectedIndexes()[0].data())

                if (
                    splitted_target_path[-2] == "scripts"
                    or splitted_target_path[-2] == "src"
                    and file_from_tree != ""
                ):
                    path = self.ui.textEdit_47.toPlainText()
                    rospy_directory_and_file_name = path + file_from_tree
                    self.ui.listWidget_26.addItem(rospy_directory_and_file_name)
                    RUN_ORDER_LIST_JUST_PATH.append(path)
                    RUN_ORDER_LIST_JUST_PATH.append(file_from_tree)

                else:
                    message_box = QMessageBox()
                    message_box.setIcon(QMessageBox.Critical)
                    message_box.setText(
                        "Check the folder and the package!\nPlease be sure to open scripts folder!"
                    )
                    message_box.setWindowTitle("Caution!")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()

            except:
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Critical)
                message_box.setText("Please select a file!")
                message_box.setWindowTitle("Warning!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

        if btnName == "select_trgt_btn":
            global ROS_SOURCE_CODE

            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("*.py *.launch")

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                if file_name[0].endswith(".py") or file_name[0].endswith(".launch"):

                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()

                        directory_split = file_name[0].split("/")
                        ros_file_name = directory_split[-1]

                        self.ui.label_86.setText(ros_file_name)
                        directory_split.pop(-1)

                        ros_launch_directory = ""

                        for i in directory_split:
                            ros_launch_directory += i + "/"

                        self.ui.textEdit_47.setPlainText(ros_launch_directory)
                        ROS_SOURCE_CODE = data
                        splitted_ros_source_codes = ROS_SOURCE_CODE.split("\n")
                        self.ui.listWidget_32.addItems(splitted_ros_source_codes)

                    model = QFileSystemModel()
                    model.setRootPath(ros_launch_directory)

                    self.ui.treeView.setModel(model)
                    self.ui.treeView.setRootIndex(model.index(ros_launch_directory))
                    self.ui.treeView.setSortingEnabled(True)
                    self.ui.treeView.hideColumn(1)
                    self.ui.treeView.hideColumn(2)
                    self.ui.treeView.hideColumn(3)

                else:
                    message_box = QMessageBox()
                    message_box.setIcon(QMessageBox.Critical)
                    message_box.setText(
                        "Please be sure to selected .py or .launch file!"
                    )
                    message_box.setWindowTitle("Attention!")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()

        if btnName == "remove_order_btn":

            def remove_ros():
                row = self.ui.listWidget_26.currentRow()
                self.ui.listWidget_26.takeItem(row)

            remove_ros()

        if btnName == "add_ros_btn":

            def fault_select_ros():
                global ZIPPED_ROS_LIST
                ZIPPED_ROS_LIST = []

                is_text_full = self.ui.textEdit_33.toPlainText()

                if is_text_full:
                    try:
                        selected_line = self.ui.listWidget_33.currentItem().text()
                        selected_fault = self.ui.listWidget_34.currentItem().text()

                        selected_line_text = "Line: " + selected_line
                        selected_fault_text = "\tFault: " + selected_fault

                        ZIPPED_ROS_LIST.append(selected_line)
                        ZIPPED_ROS_LIST.append(selected_fault)

                        selected_line_and_fault = (
                            selected_line_text + selected_fault_text
                        )

                        line_and_fault = selected_line_and_fault.split("\n")

                        self.ui.listWidget_35.addItems(line_and_fault)

                    except AttributeError() or TypeError():
                        print("Error!")

            fault_select_ros()

        if btnName == "ros_slct_fiplan":
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter(("*.json"))

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                if file_name[0].endswith(".json"):
                    directory = file_name[0]
                    new_file_name = directory.split("/")
                    ros_fi_plan_name = new_file_name[-1]
                    name_and_path = ros_fi_plan_name + "    Directory: " + directory
                    self.ui.listWidget_36.addItem(name_and_path)
                    fi_plan_directory_list.append(name_and_path)

        if btnName == "ros_fiplan_remove":

            def ros_fiplan_remove():
                fi_plan_directory_list = []

                if fi_plan_directory_list:
                    row = self.ui.listWidget_36.currentRow()
                    self.ui.listWidget_36.takeItem(row)
                    fi_plan_directory_list.pop(row)

            ros_fiplan_remove()

        if btnName == "ros_test_case":
            ros_source_code_list_count = self.ui.listWidget_10.count()
            self.ui.stackedWidget.setCurrentWidget(self.ui.rospagetest)
            self.ui.leftMenuBg.hide()
            self.ui.titleRightInfo.setText("CODE SNIPPETS - CREATE CUSTOM SNIPPETS")
            if ros_source_code_list_count > 0:
                for line_number in range(0, ros_source_code_list_count):
                    ros_line_content = self.ui.listWidget_10.item(line_number).text()
                    self.ui.listWidget_20.addItem(ros_line_content)

        if btnName == "open_ros_test_case":
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("*.py *.launch *.test")

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                if (
                    file_name[0].endswith(".py")
                    or file_name[0].endswith(".launch")
                    or file_name[0].endswith(".test")
                ):

                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()
                        self.ui.textEdit_43.setPlainText(file_name[0])
                        self.ui.textEdit_12.setPlainText(data)

                else:
                    QMessageBox().setIcon(QMessageBox.Critical)
                    QMessageBox().setText(
                        "Please be sure to selected .py/.launch/.test file!"
                    )
                    QMessageBox().setWindowTitle("Attention!")
                    QMessageBox().setStandardButtons(QMessageBox.Ok)
                    QMessageBox().exec()

        if btnName == "ros_try_test_case":

            roscore_process = subprocess.Popen(["roscore"])
            time.sleep(3)

            cmd = "rostest eva_security_test evasec_test.test"

            ros_process = subprocess.getoutput(cmd)
            try:
                roscore_process.wait(timeout=5)
            except subprocess.TimeoutExpired:

                roscore_process.terminate()

            self.ui.textEdit_41.setPlainText(ros_process)

        if btnName == "ros_save_test_case":
            self.ui.stackedWidget.setCurrentWidget(self.ui.rospagetest)
            self.ui.leftMenuBg.hide()
            self.ui.titleRightInfo.setText("CODE SNIPPETS - CREATE CUSTOM SNIPPETS")

        if btnName == "back_to_start":
            self.ui.stackedWidget.setCurrentWidget(self.ui.ros_page)
            self.ui.leftMenuBg.hide()
            self.ui.titleRightInfo.setText("CODE SNIPPETS - CREATE CUSTOM SNIPPETS")

        # Target ROS file is opened to apply mutation process
        if btnName == "open_target_ros":
            size_target_ros_list = self.ui.listWidget_10.count()

            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setNameFilter("*.py")

            if dialog.exec_():
                file_name = dialog.selectedFiles()
                if file_name[0].endswith(".py"):
                    if size_target_ros_list > 0:
                        # Clear the list for the new file
                        self.ui.listWidget_10.clear()

                    with open(file_name[0], mode="r", encoding="utf-8") as file:
                        data = file.read()
                        self.ui.textEdit_20.setPlainText(file_name[0])
                        ROS_SOURCE_CODE = data
                        splitted_ros_source_codes = data.split("\n")
                        self.ui.listWidget_10.addItems(splitted_ros_source_codes)

                else:
                    message_box = QMessageBox()
                    message_box.setIcon(QMessageBox.Critical)
                    message_box.setText("Please be sure to selected .py file!")
                    message_box.setWindowTitle("Attention!")
                    message_box.setStandardButtons(QMessageBox.Ok)
                    message_box.exec()

        if btnName == "remove_ros_btn":

            def remove_ros():
                global ZIPPED_ROS_LIST
                ZIPPED_ROS_LIST = []

                row = self.ui.listWidget_35.currentRow()
                self.ui.listWidget_35.takeItem(row)

                for i in range(2):
                    del ZIPPED_ROS_LIST[row]

            remove_ros()

        if btnName == "remove_ros_mutant":

            def remove_ros_mutant():
                global ROS_SOURCE_MUTANT
                ROS_SOURCE_MUTANT = []

                row = self.ui.listWidget_31.currentRow()
                row_text = self.ui.listWidget_31.item(row).text()
                self.ui.listWidget_31.takeItem(row)
                self.ui.label_81.setText(str(self.ui.listWidget_31.count()))

                if row > 0:
                    for i in range(len(ROS_SOURCE_MUTANT)):
                        if ROS_SOURCE_MUTANT[i] == row_text:
                            ROS_SOURCE_MUTANT.pop(i)
                            ROS_SOURCE_MUTANT.pop(i - 1)
                            break

            if self.ui.listWidget_31.count() > 0:
                remove_ros_mutant()

        if btnName == "scan_ros_btn":
            tam_konum = ""
            total_ros_items = []
            file_location = self.ui.textEdit_47.toPlainText()
            split_file_location = file_location.split("/")

            find_scripts_type = re.findall("scripts", split_file_location[-2])
            find_src_type = re.findall("src", split_file_location[-2])

            len_node_list = self.ui.listWidget_27.count()
            len_topic_list = self.ui.listWidget_28.count()
            len_service_list = self.ui.listWidget_29.count()
            len_param_list = self.ui.listWidget_30.count()

            for i in range(len_node_list):
                node_list_item = self.ui.listWidget_27.item(i).text()
                node_list_item = node_list_item[1:]
                total_ros_items.append(node_list_item)

            for i in range(len_topic_list):
                topic_list_item = self.ui.listWidget_28.item(i).text()
                if find_scripts_type or find_src_type:
                    topic_list_item = topic_list_item[1:]
                else:
                    topic_list_item = topic_list_item
                total_ros_items.append(topic_list_item)

            for i in range(len_service_list):
                service_list_item = self.ui.listWidget_29.item(i).text()
                service_list_item = service_list_item[1:]
                total_ros_items.append(service_list_item)

            for i in range(len_node_list):
                param_list_item = self.ui.listWidget_30.item(i).text()
                param_list_item = param_list_item[1:]
                total_ros_items.append(param_list_item)

            len_ros_code = self.ui.listWidget_32.count()

            directory = self.ui.textEdit_47.toPlainText()
            split_directory = directory.split("/")

            if split_directory[-2] == "launch":
                python_files_list = []
                launch_files_list = []

                key_list = ["type", "file"]

                def mutate_all_keys(key_data_list, konum, target_file):
                    """Mutation testing applies to  the all possible nodes"""
                    ros_launch_directory_path = self.ui.textEdit_47.toPlainText()

                    os.chdir(ros_launch_directory_path)
                    tree = ET.parse(target_file)
                    root = tree.getroot()
                    lenroot = len(root)
                    for i in range(0, lenroot):
                        dictof = root[i].attrib

                        key_list = list(dictof.keys())  # "file" keyleri

                        for target_key in key_list:
                            if target_key == "type":
                                python_files_list.append(
                                    dictof["type"]
                                )  # python dosyalarını içeren liste

                            elif target_key == "file":
                                launch_files_list.append(
                                    dictof["file"]
                                )  # launch dosyalarını içeren liste

                def open_python(konum, python_files_list):
                    is_ros_for_mutation_list_empty = self.ui.listWidget_10.count()

                    if is_ros_for_mutation_list_empty > 0:
                        target_ros_py_location = self.ui.textEdit_20.toPlainText()
                        target_ros_file_size = self.ui.listWidget_10.count()

                        for line_number in range(0, target_ros_file_size):
                            ros_file_line = self.ui.listWidget_10.item(
                                line_number
                            ).text()
                            for pattern in total_ros_items:
                                find_possible_line = re.findall(
                                    pattern, ros_file_line, re.MULTILINE
                                )
                                check_rospy = re.findall(
                                    "rospy", ros_file_line, re.MULTILINE
                                )
                                if find_possible_line and check_rospy:
                                    self.ui.listWidget_10.item(
                                        line_number
                                    ).setBackground(
                                        QtGui.QColor(102, 0, 102)
                                    )  # Mor renge boyar
                                    line_and_location = []
                                    line_and_location = [
                                        ros_file_line.strip(),
                                        " Directory: ",
                                        target_ros_py_location,
                                    ]
                                    str_line_and_location = (
                                        line_and_location[0]
                                        + line_and_location[1]
                                        + line_and_location[2]
                                    )
                                    self.ui.listWidget_33.addItem(str_line_and_location)

                    else:
                        for i in python_files_list:
                            with open(
                                os.path.join(konum, i), mode="r", encoding="utf-8"
                            ) as x_file:

                                pure_file_content = x_file.read()

                            split_file_content = pure_file_content.split("\n")

                            lstrip_lines = []

                            for line in split_file_content:
                                changed_line = line.lstrip()
                                lstrip_lines.append(changed_line)

                            for ros_code_line in lstrip_lines:
                                for pattern in total_ros_items:
                                    find_possible_line = re.findall(
                                        pattern, ros_code_line, re.MULTILINE
                                    )
                                    if find_possible_line:
                                        check_rospy = re.findall(
                                            "rospy", ros_code_line, re.MULTILINE
                                        )
                                        if check_rospy:
                                            line_and_location = []
                                            target_ros_py_location = konum + "/" + i
                                            ros_code_line = ros_code_line.lstrip()
                                            line_and_location = [
                                                ros_code_line,
                                                " Directory: ",
                                                target_ros_py_location,
                                            ]
                                            str_line_and_location = (
                                                line_and_location[0]
                                                + line_and_location[1]
                                                + line_and_location[2]
                                            )
                                            self.ui.listWidget_33.addItem(
                                                str_line_and_location
                                            )

                yeni_konum = ""

                complete_directory_path = self.ui.textEdit_47.toPlainText()

                split_complete_directory_path = complete_directory_path.split("/")

                target_file = (
                    self.ui.label_86.text()
                )  # "eva_security_patrol_start.launch"

                for i in range(0, 6):
                    tam_konum += (
                        split_complete_directory_path[i] + "/"
                    )  # "/home/ino/catkin_ws/src/eva_security/"

                mutate_all_keys(key_list, tam_konum, target_file)

                if launch_files_list:
                    for i in launch_files_list:
                        split_value = i.split("/")
                        target_file = split_value[-1]
                        mutate_all_keys(key_list, tam_konum, target_file)

                    for i in range(0, 7):
                        yeni_konum += (
                            split_complete_directory_path[i] + "/"
                        )  # "/home/ino/catkin_ws/src/eva_security/"

                    kullanilacak_konum = yeni_konum + "scripts"

                    open_python(kullanilacak_konum, python_files_list)

            else:
                for i in range(len_ros_code):
                    ros_code_line = self.ui.listWidget_32.item(i).text()
                    for pattern in total_ros_items:
                        find_possible_line = re.findall(
                            pattern, ros_code_line, re.MULTILINE
                        )
                        if find_possible_line:
                            check_rospy = re.findall(
                                "rospy", ros_code_line, re.MULTILINE
                            )
                            if check_rospy:
                                folder_name = self.ui.textEdit_47.toPlainText()
                                file_name = self.ui.label_86.text
                                complete_name = folder_name + file_name

                                ros_code_line = ros_code_line.lstrip()
                                ros_line_and_directory = (
                                    ros_code_line + " Directory: " + complete_name
                                )
                                self.ui.listWidget_33.addItem(ros_line_and_directory)

        if btnName == "mutate_ros_btn":
            global ZIPPED_ROS_LIST

            length_found_lines = self.ui.listWidget_33.count()
            length_mutant_codes_list = self.ui.listWidget_31.count()

            directory = self.ui.textEdit_47.toPlainText()
            split_directory = directory.split("/")

            if length_mutant_codes_list:
                self.ui.listWidget_31.clear()
                message_box = QMessageBox()
                message_box.setIcon(QMessageBox.Critical)
                message_box.setText("Mutants have already been updated!")
                message_box.setWindowTitle("Warning!")
                message_box.setStandardButtons(QMessageBox.Ok)
                message_box.exec()

            if length_found_lines:
                node_list = []
                topic_list = []
                service_list = []
                parameter_list = []

                len_node_list = self.ui.listWidget_27.count()
                len_topic_list = self.ui.listWidget_28.count()
                len_service_list = self.ui.listWidget_29.count()
                len_param_list = self.ui.listWidget_30.count()

                for i in range(len_node_list):
                    item = self.ui.listWidget_27.item(i).text()
                    node_list.append(item[1:])

                for i in range(len_topic_list):
                    item = self.ui.listWidget_28.item(i).text()
                    if split_directory[-2] == "scripts" or split_directory[-2] == "src":
                        topic_list.append(item[1:])
                    if split_directory[-2] == "launch":
                        topic_list.append(item)

                for i in range(len_service_list):
                    item = self.ui.listWidget_29.item(i).text()
                    service_list.append(item[1:])

                for i in range(len_param_list):
                    item = self.ui.listWidget_30.item(i).text()
                    parameter_list.append(item[1:])

                def constant_mutate_function(target_line, loc):
                    global ZIPPED_ROS_LIST
                    global POSSIBLE_MUTANT_LIST

                    ZIPPED_ROS_LIST = []
                    POSSIBLE_MUTANT_LIST = []

                    ROS_SOURCE_MUTANT = []

                    constant_list = []

                    class ConstantMutator(ast.NodeTransformer):
                        """Constant Mutator Class"""

                        def visit_Constant(self, node):
                            """The visitor function."""
                            if isinstance(node.value, str):
                                constant_target = node.value
                                constant_list.append(constant_target)

                    node = ast.parse(target_line)
                    renamer = ConstantMutator()
                    node2 = renamer.visit(node)

                    all_ros_patterns = [
                        "rospy.Sub",
                        "rospy.Pub",
                        "rospy.Log",
                        "rospy.log",
                        "rospy.Time",
                        "rospy.Dur",
                        "rospy.Rate",
                        "rospy.Par",
                        "rospy.Ser",
                        "rospy.ser",
                        "rospy.init",
                    ]

                    for ros_pattern in all_ros_patterns:
                        ros_result = re.findall(ros_pattern, target)
                        if ros_result:
                            if (
                                ros_result[0] == "rospy.Sub"
                                or ros_result[0] == "rospy.Pub"
                            ):
                                POSSIBLE_MUTANT_LIST = [
                                    "/" + self.ui.listWidget_28.item(x).text()
                                    for x in range(self.ui.listWidget_28.count())
                                ]
                            elif (
                                ros_result[0] == "rospy.Log"
                                or ros_result[0] == "rospy.log"
                            ):
                                POSSIBLE_MUTANT_LIST = [
                                    self.ui.listWidget_28.item(x).text()
                                    for x in range(self.ui.listWidget_28.count())
                                ]
                            elif ros_result[0] == "rospy.Par":
                                POSSIBLE_MUTANT_LIST = [
                                    self.ui.listWidget_30.item(x).text()
                                    for x in range(self.ui.listWidget_30.count())
                                ]
                            elif (
                                ros_result[0] == "rospy.Ser"
                                or ros_result[0] == "rospy.ser"
                            ):
                                POSSIBLE_MUTANT_LIST = [
                                    self.ui.listWidget_29.item(x).text()
                                    for x in range(self.ui.listWidget_29.count())
                                ]
                            elif ros_result[0] == "rospy.init":
                                POSSIBLE_MUTANT_LIST = [
                                    self.ui.listWidget_27.item(x).text()
                                    for x in range(self.ui.listWidget_27.count())
                                ]
                            else:
                                POSSIBLE_MUTANT_LIST = [
                                    "mutant_1",
                                    "mutant_2",
                                    "mutant_3",
                                ]

                            for i in constant_list:
                                for j in POSSIBLE_MUTANT_LIST:
                                    x = j[1:].join(target.rsplit(i, 1))
                                    if target_line != x:
                                        self.ui.listWidget_31.addItem(x)
                                        add_location(loc)
                                        ROS_SOURCE_MUTANT.append(loc)
                                        ROS_SOURCE_MUTANT.append(target_line)
                                        ROS_SOURCE_MUTANT.append(x)

                ### AST NAME MUTATOR ###

                # Funciton name is mutated by IM-FIT with using the method
                def function_name_mutator(target_line, loc):
                    """Method applies mutation for function name of ROS source codes"""
                    name_list = []

                    class NameIdMutator(ast.NodeTransformer):
                        """Name ID mutator class"""

                        def visit_Name(self, node):
                            """Method applies mutation for Name ID"""
                            target = node.id
                            if (
                                target != "rospy"
                                and target != "String"
                                and target != "args"
                                and target != "kwargs"
                            ):
                                name_list.append(target)

                    node = ast.parse(target_line)
                    renamer = NameIdMutator()
                    node2 = renamer.visit(node)

                    mutant_list = [
                        "representative_mutant_1",
                        "representative_mutant_2",
                        "representative_mutant_3",
                    ]

                    for i in name_list:
                        for j in mutant_list:
                            x = j[1:].join(target.rsplit(i, 1))
                            if target_line != x:
                                self.ui.listWidget_31.addItem(x)
                                add_location(loc)
                                ROS_SOURCE_MUTANT.append(loc)
                                ROS_SOURCE_MUTANT.append(target_line)
                                ROS_SOURCE_MUTANT.append(x)

                ### AST VALUE MUTATOR ###

                def value_mutate_function(target_line, loc):
                    class ConstantMutator(ast.NodeTransformer):
                        """Constant Mutator Class"""

                        global constant_list
                        constant_list = []

                        def visit_Constant(self, node):
                            """The visitor function."""
                            if not isinstance(node.value, str):
                                if isinstance(node.value, bool):
                                    if node.value is True:
                                        node.value = False
                                        self.generic_visit(node)
                                        return node
                                    node.value = True
                                    self.generic_visit(node)
                                    return node
                                value_number = node.value
                                random_number_for_node_value = random.randint(1, 100)
                                if value_number != random_number_for_node_value:
                                    node.value = random.randint(1, 100)
                                    return node
                                else:
                                    node.value = (random.randint(1, 100)) + 1
                                    return node
                            return node

                    node = ast.parse(target_line)
                    renamer = ConstantMutator()
                    node2 = renamer.visit(node)
                    unparsed_code = astunparse.unparse(node2)
                    unparsed_code = unparsed_code.strip()
                    if target_line != unparsed_code:
                        self.ui.listWidget_31.addItem(unparsed_code)
                        add_location(loc)
                        ROS_SOURCE_MUTANT.append(loc)
                        ROS_SOURCE_MUTANT.append(target_line)
                        ROS_SOURCE_MUTANT.append(unparsed_code)

                def add_location(loc):
                    mutant_code_list_size = self.ui.listWidget_31.count()

                    if mutant_code_list_size > 0:
                        line_of_mutant_list = self.ui.listWidget_31.item(
                            mutant_code_list_size - 1
                        ).text()
                        self.ui.listWidget_31.takeItem(mutant_code_list_size - 1)
                        new_line = line_of_mutant_list + "        Directory: " + loc
                        self.ui.listWidget_31.addItem(new_line)

                if (
                    self.ui.checkBox_9.isChecked() is True
                    and self.ui.listWidget_33.count() > 0
                ):
                    list_found_lines = []
                    list_directories = []
                    len_found_lines = self.ui.listWidget_33.count()
                    for i in range(len_found_lines):
                        found_line_and_directory = self.ui.listWidget_33.item(i).text()
                        split_found_line_and_directory = found_line_and_directory.split(
                            " Directory: "
                        )
                        item_found_lines = split_found_line_and_directory[0]
                        item_found_directory = split_found_line_and_directory[1]
                        list_found_lines.append(item_found_lines)
                        list_directories.append(item_found_directory)

                    for target_line in range(len(list_found_lines)):
                        target = list_found_lines[target_line]
                        loc = list_directories[target_line]
                        constant_mutate_function(target, loc)
                        value_mutate_function(target, loc)
                        result = re.findall("rospy.log", target)
                        if result:
                            function_name_mutator(target, loc)

                else:
                    len_zipped_ros_list = len(ZIPPED_ROS_LIST)
                    for i in range(len_zipped_ros_list):
                        if i % 2 == 1:
                            target_line = str(ZIPPED_ROS_LIST[i - 1])
                            selected_fault = str(ZIPPED_ROS_LIST[i])
                            if selected_fault == "ROS Pub-Sub Mutation":
                                find_snip = ["rospy.Sub", "rospy.Pub"]
                                for snip in find_snip:
                                    result = re.findall(snip, target_line)
                                    if result:
                                        split_found_line_and_directory = (
                                            target_line.split(" Directory: ")
                                        )
                                        target = split_found_line_and_directory[0]
                                        loc = split_found_line_and_directory[1]

                                        constant_mutate_function(target, loc)
                                        value_mutate_function(target, loc)

                            elif selected_fault == "ROS Log Mutation":
                                find_snip = ["rospy.Log", "rospy.log"]
                                for snip in find_snip:
                                    result = re.findall(snip, target_line)

                                    if result:
                                        split_found_line_and_directory = (
                                            target_line.split(" Directory: ")
                                        )
                                        target = split_found_line_and_directory[0]
                                        loc = split_found_line_and_directory[1]

                                        function_name_mutator(target, loc)
                                        value_mutate_function(target, loc)

                            elif selected_fault == "ROS Time Mutation":
                                find_snip = [
                                    "rospy.Time",
                                    "rospy.Dur",
                                    "rospy.Rate",
                                ]
                                for snip in find_snip:
                                    result = re.findall(snip, target_line)
                                    if result:
                                        split_found_line_and_directory = (
                                            target_line.split(" Directory: ")
                                        )
                                        target = split_found_line_and_directory[0]
                                        loc = split_found_line_and_directory[1]

                                        value_mutate_function(target, loc)

                            elif selected_fault == "ROS Parameter Mutation":
                                find_snip = ["rospy.Par"]
                                for snip in find_snip:
                                    result = re.findall(snip, target_line)
                                    split_found_line_and_directory = target_line.split(
                                        " Directory: "
                                    )
                                    target = split_found_line_and_directory[0]
                                    loc = split_found_line_and_directory[1]
                                    if result:
                                        function_name_mutator(target, loc)
                                        constant_mutate_function(target, loc)
                                        value_mutate_function(target, loc)

                            elif selected_fault == "ROS Service Mutation":
                                find_snip = ["rospy.Ser", "rospy.ser"]
                                for snip in find_snip:
                                    result = re.findall(snip, target_line)
                                    if result:
                                        split_found_line_and_directory = (
                                            target_line.split(" Directory: ")
                                        )
                                        target = split_found_line_and_directory[0]
                                        loc = split_found_line_and_directory[1]

                                        function_name_mutator(target, loc)
                                        constant_mutate_function(target, loc)
                                        value_mutate_function(target, loc)

                            elif selected_fault == "ROS Initializing Node Mutation":
                                find_snip = ["rospy.init"]
                                for snip in find_snip:
                                    result = re.findall(snip, target_line)
                                    if result:
                                        split_found_line_and_directory = (
                                            target_line.split(" Directory: ")
                                        )
                                        target = split_found_line_and_directory[0]
                                        loc = split_found_line_and_directory[1]
                                        constant_mutate_function(target, loc)
                                        value_mutate_function(target, loc)

            total_mutant_number = self.ui.listWidget_31.count()

            if total_mutant_number:
                self.ui.label_81.setText(str(total_mutant_number))

        #  CODE SNIPPETS FROM START PAGE

        if btnName == "btn_create_code":
            self.ui.stackedWidget.setCurrentWidget(self.ui.cSnippets)
            self.ui.leftMenuBg.hide()
            self.ui.titleRightInfo.setText("CODE SNIPPETS - CREATE CUSTOM SNIPPETS")

        if btnName == "btn_remove_snip":
            row = self.ui.listWidget_8.currentRow()
            self.ui.listWidget_8.takeItem(row)

        # CREATE CUSTOM SNIPPETS FROM START PAGE

        if btnName == "btn_create_snip":
            snippet_name = self.ui.textEdit_2.toPlainText()
            snippet_title = self.ui.textEdit_27.toPlainText()
            snippet_process = self.ui.textEdit_29.toPlainText()
            snippet_regex = self.ui.textEdit_28.toPlainText()

            created_snippet_json = {
                "Snippets": {
                    "Snippet_Name": snippet_name,
                    "Title": snippet_title,
                    "Process": snippet_process,
                    "Regex_Code": snippet_regex,
                }
            }

            json_snippet = json.dumps(created_snippet_json, indent=4)

            self.ui.textEdit_25.setPlainText(json_snippet)

        if btnName == "btn_delete_snip":
            self.ui.textEdit_2.clear()
            self.ui.textEdit_27.clear()
            self.ui.textEdit_29.clear()
            self.ui.textEdit_28.clear()
            self.ui.textEdit_25.clear()
            self.ui.textEdit_16.clear()

        if btnName == "btn_save_snip":

            is_empty_code_snippet = self.ui.textEdit_25.toPlainText()

            if is_empty_code_snippet != "" and self.ui.checkBox_6.isChecked() is True:

                snippet_name = self.ui.textEdit_2.toPlainText()
                snippet_title = self.ui.textEdit_27.toPlainText()
                snippet_process = self.ui.textEdit_29.toPlainText()
                snippet_regex = self.ui.textEdit_28.toPlainText()

                created_snippet = {
                    "Snippets": {
                        "Snippet_Name": snippet_name,
                        "Title": snippet_title,
                        "Process": snippet_process,
                        "Regex_Code": snippet_regex,
                    }
                }

                with open("code_snippets.json", mode="r+", encoding="utf-8") as file:
                    # First we load existing data into a dict.
                    file_data = json.load(file)
                    # Join new_data with file_data inside emp_details
                    file_data["code_snippets"].append(created_snippet)
                    # Sets file's current position at offset.
                    file.seek(0)
                    # convert back to json.
                    json.dump(file_data, file, indent=4)

                code_snippet_file_name = self.ui.textEdit_16.toPlainText()

                dialog = QFileDialog()
                path_name = QFileDialog.getExistingDirectory()

                code_snippet_path_and_name = os.path.join(
                    path_name, code_snippet_file_name + ".json"
                )

                created_code_snippets = self.ui.textEdit_25.toPlainText()

                with open(
                    code_snippet_path_and_name, mode="w", encoding="utf-8"
                ) as file:
                    file.write(created_code_snippets)

                with open("customSnippets.json", mode="w", encoding="utf-8") as file:
                    file.write(created_code_snippets)

                self.ui.label_60.setText("SAVED!")

                self.ui.code_snippet_list.addItem(snippet_name)

        if btnName == "btn_snip_location":
            dialog = QFileDialog()
            path_name = QFileDialog.getExistingDirectory()
            self.ui.textEdit_25.setPlainText(path_name)

        if btnName == "back_snip":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            self.ui.leftMenuBg.show()
            self.ui.titleRightInfo.setText("START")

        #  SCAN PAGE

        if btnName == "btn_back_code":
            self.ui.stackedWidget.setCurrentWidget(self.ui.start)
            UIFunctions.resetStyle(self, self.ui.btn_scan.styleSheet())
            self.ui.btn_start.setStyleSheet(
                UIFunctions.selectMenu(self.ui.btn_start.styleSheet())
            )

        patterns = []
        code_snippet_data_list = []
        painted_lines = []
        workload_function_name_list = []
        code_snippet_regex_code_list = []
        painted_line_for_mutation = []
        faultable_line_list = []

        if btnName == "btn_random_fault":
            pass

        if btnName == "btn_create_custom":
            self.ui.stackedWidget.setCurrentWidget(self.ui.customFault)
            self.ui.leftMenuBg.hide()
            self.ui.titleRightInfo.setText("FAULT INJECTION PLAN - CREATE CUSTOM FAULT")

        if btnName == "btn_remove_fault":  # Tekrar düzenlenecek
            global ZIPPED_LIST

            row = self.ui.listWidget_7.currentRow()
            self.ui.listWidget_7.takeItem(row)

            for i in range(2):
                del ZIPPED_LIST[row]

        if btnName == "btn_save_fiplan":

            global source_and_mutate_code
            selected_task_list_size = self.ui.listWidget_4.count()
            created_fault_plan_list = []

            if selected_task_list_size:
                dialog = QFileDialog()
                path_name = QFileDialog.getExistingDirectory()
                if path_name != "":
                    file_name = self.ui.textEdit_26.toPlainText() + ".json"

                mutant_code_list_length = len(source_and_mutate_code)
                source_code_directory = self.ui.source_code_directory_text.toPlainText()

                for i in range(0, mutant_code_list_length):
                    if i % 2 == 0:
                        original_code = source_and_mutate_code[i]
                    else:
                        mutant_code = source_and_mutate_code[i]

                        created_fault = {
                            "Fault": {
                                "File_Directory": source_code_directory,
                                "Source_Code": original_code,
                                "Mutate_Code": mutant_code,
                            }
                        }
                        created_fault_plan_list.append(created_fault)

                with open("faultPlans.json", mode="w", encoding="utf-8") as file:
                    fault_plan_json_format = json.dumps(
                        created_fault_plan_list, indent=4
                    )
                    file.write(fault_plan_json_format)

                text = self.ui.textEdit_26.toPlainText() + "_type_python.json"
                full_path = os.path.join(path_name, text)

                with open(full_path, mode="w", encoding="utf-8") as file:
                    fault_plan_json_format = json.dumps(
                        created_fault_plan_list, indent=4
                    )
                    file.write(fault_plan_json_format)

                split_text = full_path.split("\n")
                self.ui.listWidget_11.addItems(split_text)
                self.ui.listWidget_6.addItems(split_text)

        if btnName == "btn_remove_fiplan":
            row = self.ui.listWidget_11.currentRow()
            self.ui.listWidget_11.takeItem(row)

        # CREATE CUSTOM FAULT FROM FI PLAN

        if btnName == "btn_back_fi":
            self.ui.stackedWidget.setCurrentWidget(self.ui.fiplan)
            self.ui.leftMenuBg.show()
            self.ui.titleRightInfo.setText("FAULT INJECTION PLAN")

            created_fault_list_size = self.ui.listWidget_5.count()

            if created_fault_list_size:
                for i in range(0, created_fault_list_size):
                    created_fault_list_line = self.ui.listWidget_5.item(i).text()
                    self.ui.listWidget_3.addItem(created_fault_list_line)

        if btnName == "btn_create_fault":
            fault_name = self.ui.textEdit_11.toPlainText()
            target = self.ui.textEdit_30.toPlainText()
            changed = self.ui.textEdit_31.toPlainText()
            explanation = self.ui.textEdit_32.toPlainText()

            created_fault_json = {
                "fault": {
                    "Fault_Name": fault_name,
                    "Target_to_Change": target,
                    "Changed": changed,
                    "Explanation": explanation,
                }
            }

            json_fault = json.dumps(created_fault_json, indent=4)

            self.ui.textEdit_34.setPlainText(json_fault)

        if btnName == "btn_delete_fault":
            self.ui.textEdit_11.clear()
            self.ui.textEdit_30.clear()
            self.ui.textEdit_31.clear()
            self.ui.textEdit_32.clear()
            self.ui.textEdit_34.clear()

        if btnName == "btn_save_fault":
            if (
                self.ui.textEdit_11.toPlainText() != ""
                and self.ui.textEdit_30.toPlainText() != ""
                and self.ui.textEdit_31.toPlainText() != ""
                and self.ui.textEdit_32.toPlainText() != ""
            ):
                fault_name = self.ui.textEdit_11.toPlainText()
                target = self.ui.textEdit_30.toPlainText()
                changed = self.ui.textEdit_31.toPlainText()
                explanation = self.ui.textEdit_32.toPlainText()

                created_fault_json = {
                    "fault": {
                        "Fault_Name": fault_name,
                        "Target_to_Change": target,
                        "Changed": changed,
                        "Explanation": explanation,
                    }
                }

                with open("faultLibrary.json", mode="r+", encoding="utf-8") as file:
                    # First we load existing data into a dict.
                    file_data = json.load(file)
                    # Join new_data with file_data inside emp_details
                    file_data["all_faults"].append(created_fault_json)
                    # Sets file's current position at offset.
                    file.seek(0)
                    # convert back to json.
                    json.dump(file_data, file, indent=4)

                    json_fault = json.dumps(created_fault_json, indent=4)

                    workload_file_name = self.ui.textEdit_10.toPlainText()

                    dialog = QFileDialog()
                    path_name = QFileDialog.getExistingDirectory()

                    task_path_and_name = os.path.join(
                        path_name, workload_file_name + ".json"
                    )

                    created_fault = self.ui.textEdit_34.toPlainText()

                    with open(
                        task_path_and_name, mode="w", encoding="utf-8"
                    ) as json_file:
                        json_file.write(created_fault)

                    with open("customFaults.json", mode="w", encoding="utf-8") as file:
                        file.write(created_fault)

                    self.ui.label_61.setText("SAVED!")

                self.ui.listWidget_5.addItem(fault_name)

                self.ui.textEdit_11.clear()
                self.ui.textEdit_30.clear()
                self.ui.textEdit_31.clear()
                self.ui.textEdit_32.clear()
                self.ui.textEdit_34.clear()

            else:
                self.ui.label_61.setText("FAULT DOES NOT EXIST!")

        if btnName == "btn_remove_createdFault":
            row = self.ui.listWidget_5.currentRow()
            self.ui.listWidget_5.takeItem(row)

        # EXECUTION PAGE

        if btnName == "btn_new_exe":
            print("New execution process!!!")

        if btnName == "btn_remove_exe":
            print("Remove execution!!!")

        if btnName == "btn_select_metrics":
            self.ui.stackedWidget.setCurrentWidget(self.ui.selectMetrics)
            self.ui.leftMenuBg.hide()
            self.ui.titleRightInfo.setText("EXECUTION - METRICS")

        if btnName == "btn_start_exe":
            pass

        # SELECT METRICS FROM EXECUTION PAGE

        if btnName == "saveMetrics":
            print("Metrics Saved!!!")

        if btnName == "btn_back_exe":
            self.ui.stackedWidget.setCurrentWidget(self.ui.execution)
            self.ui.leftMenuBg.show()
            self.ui.titleRightInfo.setText("EXECUTION")

        # MONITORING PAGE

        if btnName == "btn_select_scenario":
            print("Scenario Selected")

        if btnName == "btn_run_scenario":
            print("Run The Scenario")

    # RESIZE EVENTS

    def resizeEvent(self, event):
        """Resize UI window method"""
        # UPDATE SIZE GRIPS
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS

    def mousePressEvent(self, event):
        """Mouse press event method for UI"""
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
