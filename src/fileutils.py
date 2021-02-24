"""
file-related helpers
"""

import json


#clear text from file
def clear_text_file(path):
    with open(path, "r+") as f:
        f.truncate(0)


#return number of lines in a file
def file_length(path):
    return len(open(path).readlines())


#get return json dictionary
def get_json_from_file(path):
    with open(path) as f:
        return json.load(f)
