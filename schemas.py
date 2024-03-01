from dataclasses import dataclass, field

@dataclass
class LogItem:
    # Use this class to standarize a log format.
    # then you call this class in every parser to format the output.
    module: str
    user: str = ""
    seen_at: str = ""
    action: str = ""
