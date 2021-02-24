"""
backend-y helpers
"""

import json

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