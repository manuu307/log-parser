import datetime
from schemas import LogItem

# in this example, the parser keep track of every user action in order to
# registrate the login activity.

def reg_login(line:str):
    if 'CURRENT_USER' in line:

        username = line.split('CURRENT_USER')[1].split('] "')[1].split('"')[0]
        username.lower()

        last_login = datetime.datetime.now()

        obj = LogItem(
            module="LOGIN_REG",    
            user=username,
            seen_at=last_login,
            action="unknown"
        )
        return obj
