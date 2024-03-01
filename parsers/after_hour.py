from datetime import time, datetime
from schemas import LogItem
from config import FILTER_USERS
# in this parser example, the same verifies if a user generates activity afterhours
def hour_verifier(begin_time, check_time, end_time):
    if check_time >= begin_time and check_time <= end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        #Over midnight: 
        return check_time >= begin_time or check_time <= end_time 

def afterhour_check(line:str):

    begin_time = time(21, 30)
    check_time = datetime.strptime(line.split()[2], "%H:%M:%S").time()
    end_time = time(7, 0)

    if hour_verifier(begin_time, check_time, end_time):

        username = ""

        if 'CURRENT_USER' in line:
            try:
                username = line.split('CURRENT_USER')[1].split('] "')[1].split('"')[0]
                username = username.lower()
            except IndexError:
                pass  # Ignore the error and continue
        
        if username == "" and 'USERID' in line:
            try:
                username = line.split('USERID')[1].split('] "')[1].split('"')[0]
                username = username.lower()
            except IndexError:
                pass  # Ignore the error and continue


        if username != "" and username.lower() not in FILTER_USERS:
            obj = LogItem(
                module="AFTER_HOUR",    
                user=username,
                seen_at=check_time,
                action="unknown"
            )
            return obj

