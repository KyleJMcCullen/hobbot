# hobbot.py
import os
import re

import discord
import json
import wikipedia
from dotenv import load_dotenv
from random import randint
from time import sleep

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
#CURSENT_ID = os.getenv('CURSENT_ID')
HOBBIES_CHANNEL_ID = os.getenv('HOBBIES_CHANNEL_ID')
HOBBIES_CHANNEL_NAME = "hobbies"
JSON_NO_HOBBY = "NONE"
NUM_VETOES_TO_SKIP = 3

PATH_ALL = "files/all.txt"
PATH_COMPLETE = "files/complete.json"
PATH_CURRENT = "files/current.json"
PATH_LATER = "files/later.json"
PATH_TODO = "files/todo.txt"
PATH_VETOED = "files/vetoed.json"

waiting_for_complete_confirm = False
waiting_for_veto_confirm = False
waiting_for_later_confirm = False

#hobbies channel
hobchannel = None

affirm_responses = ["yes", "y", "aye", "yeah", "yea", "ye", "ya",
        "shut the fuck up hobbot, of course i meant yes. just do it.",
        "yes please", "do it", "affirmative"]

client = discord.Client()

# - retrieve notes from a specific hobby
# - pull from "later" bin


#boot
@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name} (id: {guild.id})\n'
                f'(channel id: {HOBBIES_CHANNEL_ID})'
            )
            break


#get a channel bc idk how to use client.get_channel(int)
def get_channel(channels, channel_name):
    for channel in client.get_all_channels():
        if (channel.name == channel_name):
            return channel
    return None


#upload file given path relative to hobbot.py
async def upload_file(relPath):
    await hobchannel.send(file=discord.File(relPath))


#return number of lines in a file
def file_length(path):
    return len(open(path).readlines())


#get return json dictionary
def get_json_from_file(path):
    with open(path) as f:
        return json.load(f)


#get new hobby for the week, ensuring last hobby was closed
async def new_hobby():
    currentjson = get_json_from_file(PATH_CURRENT)

    #if we already have a hobby, don't overwrite it
    if currentjson["name"] != JSON_NO_HOBBY:
        current = currentjson["name"]
        await hobchannel.send(f"The current hobby is {current}. Use !complete, !veto, or !later to close this hobby.")
        return
    
    numhobbies = file_length(PATH_TODO)
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


#return current hobby
def get_current_hobby():
    currentjson = get_json_from_file(PATH_CURRENT)
    return currentjson["name"]


#return current hobby's vetoers
def get_current_vetoers():
    currentjson = get_json_from_file(PATH_CURRENT)
    return currentjson["vetoers"]


#return current hobby's veto count
def get_current_vetoes():
    vetoers = get_current_vetoers()
    return len(vetoers)


#return current hobby's notes
def get_current_notes():
    currentjson = get_json_from_file(PATH_CURRENT)
    return currentjson["notes"]

#print current hobby
async def current_hobby():
    current = get_current_hobby()
    vetoes = get_current_vetoes()

    if current == JSON_NO_HOBBY:
        await hobchannel.send("No current hobby. Use !newhobby to pick a new hobby.")
        return

    await hobchannel.send(f"Current hobby is {current} ({vetoes} vetoes).")


#get wikipedia blurb for topic
async def get_summary():
    topic = get_current_hobby()

    if topic == JSON_NO_HOBBY:
        await hobchannel.send("No current hobby. Use !newhobby to pick a new hobby.")
        return

    try:
        await hobchannel.send(wikipedia.summary(topic, 3))
    except wikipedia.exceptions.PageError:
        await hobchannel.send("Could not find or suggest wikipedia page for " + topic)

#clear text from file
def clear_text_file(path):
    with open(path, "r+") as f:
        f.truncate(0)

#reset current.json
def clear_current_hobby():
    newjson = {
        "name": JSON_NO_HOBBY,
        "vetoers": [],
        "notes": ""
    }

    clear_text_file(PATH_CURRENT)

    #replace with default json values
    with open(PATH_CURRENT, "w") as currentfile:
        json.dump(newjson, currentfile)


#ask for a confirmation
async def request_confirmation(type):
    current = get_current_hobby()

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


#move current hobby to another json file
def move_current_to_other_file(path):
    current = get_current_hobby()
    vetoers = get_current_vetoers()
    notes = get_current_notes()

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
    clear_current_hobby()


#complete hobby: save relevant info to complete.json, reset current.json
async def mark_current_as_complete():
    move_current_to_other_file(PATH_COMPLETE)

    current = get_current_hobby()
    await hobchannel.send(f"Completed {current}!")


#move current hobby to the "to-be-done-later" list: 
async def move_current_to_later():
    current = get_current_hobby()
    move_current_to_other_file(PATH_LATER)

    await hobchannel.send(f"We'll get back to {current} later.")


#count a veto if the player hasn't already vetoed it, and skip it if
#enough vetoes are counted
#(author is a Member or User object)
async def handle_veto(author):
    current = get_current_hobby()
    vetoes = get_current_vetoes()
    vetoers = get_current_vetoers()

    nick = author.nick
    if (nick == None):
            nick = author.name

    if (nick in vetoers):
        await hobchannel.send(f"{nick} has already vetoed {current}!")
        return

    if (vetoes+1) >= NUM_VETOES_TO_SKIP:
        move_current_to_other_file(PATH_VETOED)
        vetoersstr = ", ".join(vetoers)
        await hobchannel.send(f"{current} has been vetoed by {vetoersstr}, and {nick}!")
    else:
        vetoers.append(author.name) #use username, not nickname

        with open(PATH_CURRENT) as currentfile:
            jsondata = json.load(currentfile)
        
        jsondata["vetoers"] = vetoers

        with open(PATH_CURRENT, "w") as currentfile:
            json.dump(jsondata, currentfile)

        await hobchannel.send(f"{nick} has voted to veto {current}!")


#add a note to the current hobby
async def add_note_to_current(note, authorname):
    with open(PATH_CURRENT) as currentfile:
        jsondata = json.load(currentfile)
    
    current = get_current_hobby()
    notes = get_current_notes()
    notes += ("\n" if len(notes) > 0 else "") + note + f" ({authorname})"

    jsondata["notes"] = notes

    with open(PATH_CURRENT, "w") as currentfile:
        json.dump(jsondata, currentfile)

    await hobchannel.send(f"Added note to {current}. Full notes:\n{notes}")


#list all commands
async def list_commands():
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


#command functionality
@client.event
async def on_message(msg):
    #check to see if bot sent this message
    if (msg.author == client.user):
        return

    msgtext = msg.content
    channel = msg.channel
    
    global hobchannel
    global waiting_for_complete_confirm
    global waiting_for_later_confirm
    global waiting_for_veto_confirm

    hobchannel = get_channel(client.get_all_channels(), HOBBIES_CHANNEL_NAME)

    if (hobchannel == None):
        print ("hobchannel is None")

    #only run in hobbies channel
    if (channel != hobchannel):
        return

    #commands
    if (msgtext == "!help"):
        await list_commands()
    elif (msgtext == "!listall"):
        await upload_file(PATH_ALL)
    elif (msgtext == "!listlater"):
        await upload_file(PATH_LATER)
    elif (msgtext == "!listtodo"):
        await upload_file(PATH_TODO)
    elif (msgtext == "!listvetoed"):
        await upload_file(PATH_VETOED)
    elif (msgtext == "!newhobby"):
        await new_hobby()
    elif (msgtext in ["!currenthobby", "!current"]):
        await current_hobby()
    elif (msgtext == "!summary"):
        await get_summary()
    elif (msgtext == "!complete"):
        await mark_current_as_complete()
    elif (msgtext == "!veto"):
        await handle_veto(msg.author)
    elif (msgtext == "!later"):
        await move_current_to_later()
    elif (str.startswith(msgtext, "!addnote ")):
        await add_note_to_current(msgtext[9:], msg.author.name)
        
    #responses
    elif (waiting_for_complete_confirm and msgtext.lower() in affirm_responses):
        pass 
    elif (waiting_for_later_confirm and msgtext.lower() in affirm_responses):
        pass 
    elif (waiting_for_veto_confirm and msgtext.lower() in affirm_responses):
        pass

    #testing
    elif (msgtext == "greetings hobbot"):
        await hobchannel.send(f"greetings {msg.author.mention}")
    elif (msgtext == "hobbot, shut down"):
        await hobchannel.send("goodbye world")
        await client.logout()
    elif (msgtext == "hobbot, initiate test"):
        await hobchannel.send("testing...")
        await hobchannel.send("hobbot, shut down")

    waiting_for_complete_confirm = False
    waiting_for_later_confirm = False
    waiting_for_veto_confirm = False

#start or something?
client.run(TOKEN)