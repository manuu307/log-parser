from pipelines import Pipelines
from dataclasses import dataclass, field
from typing import Dict, List, Callable
import gzip
import os
import threading
from datetime import datetime
from local_storage.db_manage import check_file_in_database, insert_state, update_state
import re

@dataclass
class Settings:
    log_files: List[str]
    handle_state: bool = False
    parsers: List[Callable] = field(default_factory=list)
    thread_num: int = 10
    express: bool = True
    force_state_searching: bool = False

class LogParser:
    def __init__(self, run_settings: Settings):
        self.run_settings = run_settings
        self.log_files = run_settings.log_files 
        
        # verify state
        if self.run_settings.express:
            self.run_settings.handle_state = False
            self.run_settings.force_state_searching = False
        # Initialize Pipelines
        self.pipeline = Pipelines()
        # Call open pipeline when LogSpider initializes
        self.pipeline.open_pipeline()

    @staticmethod
    def open_file(file_path:str) -> Dict[str, str]:
        is_backup = False

        try:
            if ".gz" in file_path:
                log_file = gzip.open(file_path, "rt", encoding="latin-1")
                is_backup = True
            else:
                log_file = open(file_path, "rt", encoding="latin-1")
            
            return {"file":log_file, "file_path": file_path, "is_backup":is_backup}

        except TypeError as type_error:
            print("[-] Caught a TypeError: ", type_error)

        except FileNotFoundError as file_not_found_error:
            print("[-] File not found:", file_not_found_error.filename)
        

    def process_log_file(self, log_file):
        if log_file:
            # declare state management variables
            file_path_string = log_file['file_path']
            self.file_previous_state = check_file_in_database(file_path_string) 
            self.resume_line_found = False
            self.current_state = []
            self.state_handler_conditional = lambda line: self.file_previous_state and line == self.file_previous_state[2] and line_number == self.file_previous_state[3] or not self.file_previous_state 
            
            self.read_lines(log_file)

            if self.run_settings.handle_state and len(self.current_state) > 0:

                values_to_save = (file_path, str(current_state[0]), current_state[1])
                
                self.save_state(file_path_string, values_to_save)
            
            else:

                if self.run_settings.force_state_searching:
                    print("[!] Could't found state in this file")
                    print("[*] Force state searching in backup files that goes by the same name under the same path...")
                    self.auto_search_state_line(file_path_string)

    def read_lines(self, file, watch_state=True):
        # start processing lines
        for line_number, line_value in enumerate(file['file'], start=1):
            line = str(line_value).strip()
            
            # state verifications
            if self.state_handler_conditional(line): 
                self.resume_line_found = True

            if self.run_settings.express or self.resume_line_found:
                self.current_state = [line, line_number] 
                
                # parsing line
                for parser in self.run_settings.parsers:
                    parser_result = parser(line)
                    
                    # send trough pipeline
                    self.pipeline.middle_pipeline(data=parser_result)

    def run(self):
        threads = []

        for file in self.log_files:
            if len(threads) >= self.run_settings.thread_num:
                # If the maximum number of threads is reached, wait for them to finish
                for thread in threads:
                    thread.join()
                threads = []  # Reset threads List
            
            log_file = self.open_file(file)
            thread = threading.Thread(target=self.process_log_file, args=(log_file,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        
        # Call end pipeline when LogSpider finishes
        self.pipeline.end_pipeline()
        print("[!] Done!")

    def save_state(self, file_path:str, values_to_save:list):
        # this will manage
        if check_file_in_database(file_path):
            update_state(*values_to_save)
            print('[*] State updated for:', file_path)
        else:
            insert_state(*values_to_save) 
            print('[*] State saved for:', file_path)

    def auto_search_state_line(self, log_file):
        # this function must search for the state line to resume the process left, even if it has to look into backup log files
        queue_files = []

        print("[*] Identifying file name...")
        file_name = None
        pattern = r"([^/']+)'?$"
    
        # Use re.search to find the match
        match = re.search(pattern, log_file)
    
        if match:
            file_name = match.group(1)  # Extract the matched file name

        print('[!] File name identified:', file_name)
        # list all files from the log_path folder
        log_path_file_list = []
        # ...
        # extract all the files that has "file_name" in it's name from the previous List
