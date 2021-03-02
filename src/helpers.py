"""
backend-y helpers
"""

import datetime
import json
import re

from constants import JSON_NO_HOBBY
from constants import PATH_CURRENT
import infogetters as info
import fileutils as futils


#reset current.json
def clear_current_hobby(hobchannel):
    newjson = {
        "name": JSON_NO_HOBBY,
        "vetoers": [],
        "notes": ""
    }

    futils.clear_text_file(PATH_CURRENT)

    #replace with default json values
    with open(PATH_CURRENT, "w") as currentfile:
        json.dump(newjson, currentfile)


#move current hobby to another json file
def move_current_to_other_file(path, hobchannel):
    current = info.get_current_hobby_name()
    vetoers = info.get_current_vetoers()
    notes = info.get_current_notes()

    #create new entry with info from current hobby
    newentry = {current: {"vetoers": vetoers, "notes": notes}}


    #get dict of completed hobbies
    with open(path) as f:
        filejson = json.load(f)
    
    #add now-completed hobby to list of completed hobbies
    filejson.update(newentry)

    #write back to file
    with open(path, "w") as f:
        json.dump(filejson, f)

    #reset current hobby
    clear_current_hobby(hobchannel)


#move current hobby to another json file
def move_current_to_other_file_with_date(path, hobchannel):
    current = info.get_current_hobby_name()
    vetoers = info.get_current_vetoers()
    notes = info.get_current_notes()
    date = str(datetime.date.today())

    #create new entry with info from current hobby
    newentry = {current: {"vetoers": vetoers, "notes": notes, "date": date}}


    #get dict of completed hobbies
    with open(path) as f:
        filejson = json.load(f)
    
    #add now-completed hobby to list of completed hobbies
    filejson.update(newentry)

    #write back to file
    with open(path, "w") as f:
        json.dump(filejson, f)

    #reset current hobby
    clear_current_hobby(hobchannel)


#return dict as string in nice format
#(from https://stackoverflow.com/a/3229493)
def prettify_dict(d, indent=0):
    outstr = ""

    for key, value in d.items():
        outstr += '\t' * indent + str(key) + "\n"
        if isinstance(value, dict):
            outstr += prettify_dict(value, indent+1)
        else:
            outstr += '\t' * (indent+1) + str(value) + "\n"

    return outstr


#add <angled brackets> around urls, return the string
def unembed_links(string):
    #match url, from https://www.geeksforgeeks.org/python-check-url-string/
    urls = re.findall(r'(https?://\S+)', string)
    for url in urls:
        string = string.replace(url, f"<{url}>")
    
    return string


""" unused, but holding on to it just in case
#ask for a confirmation
async def request_confirmation(type, hobchannel):
    current = info.get_current_hobby_name()

    if (type == "complete"):
        await hobchannel.send(f"Really finished with {current}? Make sure to add any notes **before** confirming.")
        global waiting_for_complete_confirm
        waiting_for_complete_confirm = True
    elif (type == "veto"):
        await hobchannel.send(f"Really veto {current}?")
        global waiting_for_veto_confirm
        waiting_for_veto_confirm = True
    else:
        await hobchannel.send(f"Really do {current} later?")
        global waiting_for_later_confirm
        waiting_for_later_confirm = True
"""