from pipelines import Pipelines
from dataclasses import dataclass, field
from typing import Dict, List, Callable
import gzip
import os
import threading
from datetime import datetime

@dataclass
class Settings:
    log_files: List[str]
    save_state_file: str
    parsers: List[Callable]
    thread_num: int = 10
    thread_max: int = 10
    fresh_start: bool = True

class LogParser:
    def __init__(self, run_settings: Settings):
        self.run_settings = run_settings
        self.log_files = run_settings.log_files 
        # verify state and if file exist
        self.fresh_start = True
        # Check if resume file exists
        if not os.path.exists(run_settings.save_state_file):
            with open(run_settings.save_state_file, 'w') as file:
                print("Created file:", file)

        with open(run_settings.save_state_file, 'r') as resume_file:
            self.resume_line = str(resume_file.read().strip())
            if self.resume_line != "":
                self.fresh_start = False
        
        # Initialize Pipelines
        self.pipeline = Pipelines()
        # Call open pipeline when LogSpider initializes
        self.pipeline.open_pipeline()

    @staticmethod
    def open_file(file_path:str) -> Dict[str, str]:
        is_backup = False
        if ".gz" in file_path:
            log_file = gzip.open(file_path, "rt", encoding="latin-1")
            is_backup = True
        else:
            log_file = open(file_path, "rt", encoding="latin-1")
        
        return {"file":log_file, "is_backup":is_backup}

    def process_log_file(self, log_file):
        for line_number, line_value in enumerate(log_file['file'], start=1):
            line = str(line_value).strip()

            # Middle triggers
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
