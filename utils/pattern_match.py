# this util file must be useful tu create regexp 
# in order to find useful data

import re

# example of a date regexp
def date_regex(line:str):
    date_pattern = re.compile(r'\b(?:\d{1,2}[-/ ]\d{1,2}[-/ ](?:\d{2}|\d{4})|\d{1,2} \d{2} \d{4})\b')
    result = date_pattern.search(line).group()
    return result

# example of a user regexp
def user_regex(line:str):
    user_pattern = re.compile(r'@[\w_]+') 
    result = user_pattern.search(line).group()
    return result
    

# output examples:
print(date_regex("some random string 10/01/2024 r4nd0m 57-r*1!/n6 m1x3d"))
print(date_regex("just another format 25/12/24 for dates"))
print(date_regex("have you seen a date 24-12-24 here?"))
print(date_regex("what date 10 01 2024"))

print(user_regex('there is a user @userexample in this sentence'))
