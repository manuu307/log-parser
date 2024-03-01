import time
from datetime import datetime
from dataclasses import asdict
from utils.email import EmailData, EmailHandler
from config import EMAIL_SERVER, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD 

def report_email(text:str, subject:str, to:str):
    email_data = EmailData(
        text=text,
        from_email=EMAIL_USER,
        to_email=to,
        subject=subject,
        server=EMAIL_SERVER,
        port=EMAIL_PORT,
        username=EMAIL_USER,
        password=EMAIL_PASSWORD
    )
    send_email = EmailHandler(email_data).send_email()

class Pipelines:
    def __init__(self):
        """STATS"""
        self.stats_item_count = 0
        self.stats_total_processed_lines = 0
        self.stats_start = 0
        self.stats_finish =  0
        self.stats_time_lapse = 0

        """USER ADDITIONAL OPTIONS HERE"""
        # in this example the stalker items are a list of accumulated logs
        # by the parsers/stalk_user.py parser that will be sent in an email
        # in a form of report
        self.stalker_items = []

    def open_pipeline(self):
        # modify the initial stats that you need
        self.stats_start = datetime.now()

        # actions to perform on initialization
        # for example open database connection
        # and use the connector in the middle Pipelines
        self.db_connector = ''
        print('openning database connector...')
        print('initializing logparser...')

    def middle_pipeline(self, data):
        # perform any action you need in the middle, using the data from parsers
        # for example format data and insert into database using the parsers result
        # additionally you can modify the stats needed in this stage
        
        self.stats_total_processed_lines += 1 # stat
        if data is not None:
            self.stats_item_count += 1 # stat
            
            # perform the action needed for any individual parser
            module = data.module
            if module == 'STALKER':
                self.stalker_items.append(asdict(data))

    def end_pipeline(self):
        """STATS RETURNED"""
        # this stats examples are generated in the entire process 
        # and returned once the process finishes
        self.stats_finish = datetime.now()
        self.stats_time_lapse = self.stats_finish - self.stats_start
        
        # declare stats object to return at the end
        stats = {
            "total_processed_lines": self.stats_total_processed_lines,
            "item_count":self.stats_item_count,
            "start":self.stats_start,
            "finish":self.stats_finish,
            "time_lapse":self.stats_time_lapse
        }

        """ USER ADDITIONAL OPTIONS HERE"""
        # you can add any functionality you want when the process finishes
        # in this example we are sending an email report
        report_email(
            text="Testing log spider", 
            subject="This is a test", 
            to="email@to.com"
        )
        
        """ PRINT STATS """
        print('Stats {}'.format(stats))

