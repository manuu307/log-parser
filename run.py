from log_parser import LogParser, Settings
from parsers.after_hour import afterhour_check
from parsers.stalk_user import stalk_user
from parsers.reg_login import reg_login
from config import LOG_FILE_PATHS

# declare the LogParser settings to start running
run_settings = Settings(
    log_files=LOG_FILE_PATHS,
    express=False,
    handle_state=True,
    parsers=[stalk_user, reg_login, afterhour_check],
    force_state_searching=True
    )

LogParser(run_settings).run()

