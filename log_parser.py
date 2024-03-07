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
        log_file = None

        try:
            if file_path.endswith('.gz'):
                log_file = gzip.open(file_path, "rt", encoding="latin-1")
                is_backup = True
            else:
                log_file = open(file_path, "rt", encoding="latin-1")
            
            return {"file":log_file, "file_path": file_path, "is_backup":is_backup}

        except TypeError as type_error:
            print("[-] Caught a TypeError: ", type_error)

        except FileNotFoundError as file_not_found_error:
            print("[-] File not found:", file_not_found_error.filename)
        

    def process_log_file(self, log_file, force_state_file_name=None):
        if log_file:
            # declare state management variables
            file_path_string = log_file['file_path'] if force_state_file_name is None else force_state_file_name
            self.file_previous_state = check_file_in_database(file_path_string)
            self.current_state = []
            self.state_handler_conditional = lambda line: self.file_previous_state is not None and line == self.file_previous_state[2] or not self.file_previous_state 
            #self.state_handler_conditional = lambda line: self.file_previous_state is not None and line == self.file_previous_state[2] and line_number == self.file_previous_state[3] or not self.file_previous_state 
            
            self.read_lines(log_file)

            if self.run_settings.handle_state and self.resume_line_found:
                
                if len(self.current_state) > 0:
                    values_to_save = (file_path_string, str(self.current_state[0]), self.current_state[1])
                    self.save_state(file_path_string, values_to_save)
                else:
                    print("[!] Nothing to save")
            
            else:

                if self.run_settings.force_state_searching:
                    print("[-] Could't found state in this file")
                    print("[!] Force state searching in backup files that goes by the same name under the same path...")
                    self.auto_search_state_line(file_path_string)

    def read_lines(self, file_path, looking_for_resume_line_only=False):
        ## testing
        if 'gz' in file_path['file_path']:
            file_path = self.open_file(file_path['file_path'])

        self.resume_line_found = False
        # start processing lines
        for line_number, line_value in enumerate(file_path['file'], start=1):
            line = str(line_value).strip()
            
            # state verifications
            if self.state_handler_conditional(line):
                self.resume_line_found = True
            
                if looking_for_resume_line_only:
                    break

            if self.run_settings.express or self.resume_line_found:
                self.current_state = [line, line_number] 
                
                # parsing line
                for parser in self.run_settings.parsers:
                    parser_result = parser(line)
                    
                    # send trough pipeline
                    self.pipeline.middle_pipeline(data=parser_result)

        return {"resume_line_found":self.resume_line_found}

    def save_state(self, file_path:str, values_to_save:list):
        # this will manage
        if check_file_in_database(file_path):
            update_state(*values_to_save)
            print('[+] State updated for:', file_path)
        else:
            insert_state(*values_to_save) 
            print('[+] State saved for:', file_path)
    
    def auto_search_state_line(self, log_file_path):
        # this function must search for the state line to resume the process left, even if it has to look into backup log files
        queue_files = []

        print("[*] Identifying file name...")
        file_name = None
        pattern = r"([^/']+)'?$"
    
        # Use re.search to find the match
        match = re.search(pattern, log_file_path)
    
        if match:
            file_name = match.group(1)  # Extract the matched file name

        folder_path = log_file_path.split(file_name)[0]
        
        print('[+] File name identified:', file_name)

        
        print('[*] Looking for the last scanned file...')
        last_scanned_file = ""
        last_scanned_file_name = ""

        # extract all the files that has "file_name" in it's name from the previous List
        related_log_file_list = self.list_log_files_in_path(folder_path, file_name)

        for file in related_log_file_list:
            print('[*] Trying', file)
            
            file_content = self.open_file(os.path.join(folder_path, file))
            find_resume_line = self.read_lines(file_path=file_content, looking_for_resume_line_only=True)
            
            if find_resume_line["resume_line_found"]:
                last_scanned_file = file_content
                last_scanned_file_name = file
                print('[+] Last scanned file founded! It was:', file)
                break

        if last_scanned_file == "":
            print('[-] Last scanned file not found. Verify manually')
        else:
            print('[*] Resuming process from that file to the last one.')
            # create a file list from last_scanned_file to actual log file and loop on it
            found_file_index = related_log_file_list.index(last_scanned_file_name)
            for index in range(found_file_index, -1, -1):
                print("[*] Processing file:", related_log_file_list[index])
                file_content = self.open_file(os.path.join(folder_path, file))
                self.process_log_file(file_content, force_state_file_name=log_file_path)


    def list_log_files_in_path(self, folder_path, file_name):
        # get all the files related to the specified log file 
        files = os.listdir(folder_path)
        related_files = [file for file in files if os.path.isfile(os.path.join(folder_path, file)) and file_name in file]
        # get the realted file list in reverse order, from the last to the first
        related_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
        
        return related_files

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
        print("[+] Done!")


