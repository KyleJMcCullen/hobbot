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

PATH_ALL = "files/all.txt"
PATH_COMPLETE = "files/complete.json"
PATH_CURRENT = "files/current.json"
PATH_LATER = "files/later.txt"
PATH_TODO = "files/todo.txt"
PATH_VETOED = "files/vetoed.txt"

waiting_for_complete_confirm = False
waiting_for_veto_confirm = False
waiting_for_later_confirm = False

#hobbies channel
hobchannel = None

affirm_responses = ["yes", "y", "aye", "yeah", "yea", "ye", "ya",
        "shut the fuck up hobbot, of course i meant yes. just do it.",
        "yes please", "do it", "affirmative"]

client = discord.Client()


##################################################
##  ADD NOTES CAPABILITY FOR COMPLETED HOBBIES  ##
##################################################


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
            "vetoes": 0,
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


#return (current hobby, vetoes)
def get_current_hobby():
    currentjson = get_json_from_file(PATH_CURRENT)
    return currentjson["name"]


#return current hobby's vetoes
def get_current_vetoes():
    currentjson = get_json_from_file(PATH_CURRENT)
    return currentjson["vetoes"]


#return current hobby's vetoers
def get_current_vetoers():
    currentjson = get_json_from_file(PATH_CURRENT)
    return currentjson["vetoers"]


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
    topic = get_current_hobby

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
        "vetoes": 0,
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


#complete hobby: save relevant info to complete.json, reset current.json
async def mark_current_as_complete():
    current = get_current_hobby()
    vetoes = get_current_vetoes()
    vetoers = get_current_vetoers()
    notes = get_current_notes()

    #create new entry with info from current hobby
    newentry = {current: {"vetoes": vetoes, "vetoers": vetoers, "notes": notes}}

    #get dict of completed hobbies
    with open(PATH_COMPLETE) as completefile:
        completed = json.load(completefile)
    
    #add now-completed hobby to list of completed hobbies
    completed.update(newentry)

    #write back to file
    with open(PATH_COMPLETE, "w") as completefile:
        json.dump(completed, completefile)

    #reset current hobby
    clear_current_hobby()

    await hobchannel.send(f"{current} completed!")


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
    if (msgtext == "!listall"):
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
        await request_confirmation("complete")
        return #don't reset waiting-for-confirm booleans
    elif (msgtext == "!veto"):
        await (request_confirmation("veto"))
        return #don't reset waiting-for-confirm booleans
    elif (msgtext == "!later"):
        await request_confirmation("request")
        return #don't reset waiting-for-confirm booleans
        
    #responses
    elif (waiting_for_complete_confirm and msgtext.lower() in affirm_responses):
        await mark_current_as_complete()
    elif (waiting_for_later_confirm and msgtext.lower() in affirm_responses):
        pass
    elif (waiting_for_later_confirm and msgtext.lower() in affirm_responses):
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