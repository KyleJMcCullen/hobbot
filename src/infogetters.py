"""
getters to return information about current hobby
"""

from constants import PATH_CURRENT
import fileutils as futils


#return current hobby
def get_current_hobby_name():
    currentjson = futils.get_json_from_file(PATH_CURRENT)
    return currentjson["name"]


#return current hobby's vetoers
def get_current_vetoers():
    currentjson = futils.get_json_from_file(PATH_CURRENT)
    return currentjson["vetoers"]


#return current hobby's veto count
def get_current_vetoes():
    vetoers = get_current_vetoers()
    return len(vetoers)


#return current hobby's notes
def get_current_notes():
    currentjson = futils.get_json_from_file(PATH_CURRENT)
    return currentjson["notes"]