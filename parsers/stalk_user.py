from schemas import LogItem
from datetime import datetime
from config import WATCH_USERS

# in this example, this parser follows every action performed by a user.
# the results are being acumulated in pipelines and then report alltogether by email
def stalk_user(line:str):
    if WATCH_USERS[0].lower() in line.lower():
        
        obj = {}

        try:
            table = line.split("OBJ$NAME")[1].split('" ')[0].split('] "')[1]
            obj = LogItem(
                module="STALKER",    
                user=WATCH_USERS[0],
                seen_at=str(datetime.now()),
                action=table
            )
        except Exception as e:
            obj = LogItem(
                module="STALKER",    
                user=WATCH_USERS[0],
                seen_at=str(datetime.now()),
                action='unknown'
            )

        return obj
 
