"""
functions called as the result of a user typing a !command
"""

import discord
import json
from random import randint
from time import sleep
import wikipedia

import fileutils as futils
import helpers as helpers
import infogetters as info

from constants import JSON_NO_HOBBY
from constants import NUM_VETOES_TO_SKIP
from constants import PATH_COMPLETE
from constants import PATH_CURRENT
from constants import PATH_LATER
from constants import PATH_TODO
from constants import PATH_VETOED


#add a note to the current hobby
async def add_note_to_current(note, authorname, hobchannel):
    jsondata = futils.get_json_from_file(PATH_CURRENT)
    
    current = info.get_current_hobby_name()
    notes = info.get_current_notes()
    notes += ("\n" if len(notes) > 0 else "") + note + f" ({authorname})"

    jsondata["notes"] = notes

    with open(PATH_CURRENT, "w") as currentfile:
        json.dump(jsondata, currentfile)

    await hobchannel.send(f"Added note to {current}. Full notes:\n{notes}")


#count a veto if the player hasn't already vetoed it, and skip it if
#enough vetoes are counted
#(author is a Member or User object)
async def handle_veto(author, hobchannel):
    current = info.get_current_hobby_name()
    vetoes = info.get_current_vetoes()
    vetoers = info.get_current_vetoers()

    nick = author.nick
    if (nick == None):
            nick = author.name

    if (nick in vetoers):
        await hobchannel.send(f"{nick} has already vetoed {current}!")
        return

    if (vetoes+1) >= NUM_VETOES_TO_SKIP:
        helpers.move_current_to_other_file(PATH_VETOED, hobchannel)
        vetoersstr = ", ".join(vetoers)
        await hobchannel.send(f"{current} has been vetoed by {vetoersstr}, and {author.name}!")
    else:
        vetoers.append(author.name) #use username, not nickname

        jsondata = futils.get_json_from_file(PATH_CURRENT)
        
        jsondata["vetoers"] = vetoers

        with open(PATH_CURRENT, "w") as currentfile:
            json.dump(jsondata, currentfile)

        await hobchannel.send(f"{nick} has voted to veto {current}!")


#list all commands
async def list_commands(hobchannel):
    commands = {
        "!help": "List all commands",
        "!listall": "Get complete list of all hobbies",
        "!listlater": "Get list of hobbies to be completed later",
        "!listtodo": "Get list of hobbies that have yet to be completed",
        "!listvetoed": "Get list of vetoed hobbies",
        "!newhobby": "Pull a new hobby from the todo list",
        "!current *or* !currenthobby": "Get name and veto count of current hobby",
        "!summary": "Try to pull a summary of the current hobby from Wikipedia",
        "!complete": "Move current hobby to the list of completed hobbies",
        "!veto": f"Vote to veto a hobby ({NUM_VETOES_TO_SKIP} needed to skip)",
        "!later": "Move current hobby to the list of hobbies to be completed later",
        "!addnote [note]": "Add a note to the current hobby"
    }

    outstr = ""

    for key, value in sorted(commands.items()):
        if (outstr != ""):
            outstr += "\n"
        outstr += f"{key}: {value}"

    await hobchannel.send(outstr)


# move current hobby to the "to-be-done-later" list: 
async def move_current_to_later(hobchannel):
    current = info.get_current_hobby_name()
    helpers.move_current_to_other_file(PATH_LATER, hobchannel)

    await hobchannel.send(f"We'll get back to {current} later.")


#complete hobby: save relevant info to complete.json, reset current.json
async def mark_current_as_complete(hobchannel):
    current = info.get_current_hobby_name()
    helpers.move_current_to_other_file_with_date(PATH_COMPLETE, hobchannel)

    await hobchannel.send(f"Completed {current}!")


#get new hobby for the week, ensuring last hobby was closed
async def new_hobby(hobchannel):
    currentjson = futils.get_json_from_file(PATH_CURRENT)

    #if we already have a hobby, don't overwrite it
    if currentjson["name"] != JSON_NO_HOBBY:
        current = currentjson["name"]
        await hobchannel.send(f"The current hobby is {current}. Use !complete, !veto, or !later to close this hobby.")
        return
    
    numhobbies = futils.file_length(PATH_TODO)
    newhobbynum = randint(1, numhobbies)

    with open(PATH_TODO, "r") as todofile:
        lines = todofile.readlines()

    #pick a new hobby
    newhobby = lines[newhobbynum].strip()

    #remove the new hobby from the todo list
    with open(PATH_TODO, "w") as todofile:
        for line in lines:
            if line.strip() != newhobby:
                todofile.write(line)

    with open(PATH_CURRENT, "w") as currentfile:
        newjson = {
            "name": newhobby,
            "vetoers": [],
            "notes": ""
        }
        currentfile.write(json.dumps(newjson))

    lastmsg = await hobchannel.send("Next week's hobby is")
    sleep(1)
    await lastmsg.edit(content="Next week's hobby is .")
    sleep(1)
    await lastmsg.edit(content="Next week's hobby is . .")
    sleep(1)
    await lastmsg.edit(content="Next week's hobby is . . .")
    sleep(1)

    await hobchannel.send(f"\~\~\~\~\~\~\~\~\~\~ {newhobby}! \~\~\~\~\~\~\~\~\~\~")


#pick specific hobby from 'later' list
async def pick_hobby_from_later(hobby, hobchannel):
    currentjson = futils.get_json_from_file(PATH_CURRENT)

    #if we already have a hobby, don't overwrite it
    if currentjson["name"] != JSON_NO_HOBBY:
        current = currentjson["name"]
        await hobchannel.send(f"The current hobby is {current}. Use !complete, !veto, or !later to close this hobby.")
        return
        
    laterjson = futils.get_json_from_file(PATH_LATER)
    
    #existing hobby info from later.json 
    try:
        newhobbyjson = laterjson[hobby]
    except KeyError:
        await hobchannel.send(f"Could not find {hobby} in later.json (was KeyError).")
        return

    #idk if i need this still
    if (newhobbyjson == None):
        await hobchannel.send(f"Could not find {hobby} in later.json (was None).")
        return

    print("\n\nlaterjson: " + (laterjson))
    print("\n" + str(newhobbyjson) + "\n\n")

    with open(PATH_CURRENT, "w") as currentfile:
        newjson = {
            "name": hobby.capitalize(),
            "vetoers": laterjson["vetoers"],
            "notes": laterjson["notes"]
        }
        currentfile.write(json.dumps(newjson))
    
    await hobchannel.send(f"{hobby} has been picked as the new hobby!")


#print current hobby
async def print_current_hobby(hobchannel):
    current = info.get_current_hobby_name()
    vetoes = info.get_current_vetoes()

    if current == JSON_NO_HOBBY:
        await hobchannel.send("No current hobby. Use !newhobby to pick a new hobby.")
        return

    await hobchannel.send(f"Current hobby is {current} ({vetoes} vetoes).")


#get wikipedia blurb for topic
async def print_summary(hobchannel):
    topic = info.get_current_hobby_name()

    if topic == JSON_NO_HOBBY:
        await hobchannel.send("No current hobby. Use !newhobby to pick a new hobby.")
        return

    try:
        await hobchannel.send("<" + wikipedia.page(topic).url + ">\n" + wikipedia.summary(topic, 3))
    except wikipedia.exceptions.PageError:
        await hobchannel.send("Could not find or suggest wikipedia page for " + topic)


#upload file given path relative to hobbot.py
async def upload_file_to_channel(relPath, channel):
    await channel.send(file=discord.File(relPath))