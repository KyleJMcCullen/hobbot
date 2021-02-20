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
PATH_COMPLETE = "files/complete.txt"
PATH_CURRENT = "files/current.json"
PATH_LATER = "files/later.txt"
PATH_TODO = "files/todo.txt"
PATH_VETOED = "files/vetoed.txt"

client = discord.Client()

##################################################
## ADD SUMMARY CAPABILITY FOR COMPLETED HOBBIES ##
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
async def upload_file(channel, relPath):
    await channel.send(file=discord.File(relPath))

#return number of lines in a file
def file_length(path):
    return len(open(path).readlines())

#get return json dictionary
def get_json_from_file(path):
    with open(path) as f:
        return json.load(f)

#get new hobby for the week, ensuring last hobby was closed
async def new_hobby(hobchannel):
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
            "vetoes": 0
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

#print current hobby
async def current_hobby(hobchannel):
    currentjson = get_json_from_file(PATH_CURRENT)

    if currentjson["name"] == JSON_NO_HOBBY:
        await hobchannel.send("No current hobby. Use !newhobby to pick a new hobby.")
        return
    
    current = currentjson["name"]
    vetoes = currentjson["vetoes"]

    await hobchannel.send(f"Current hobby is {current} ({vetoes} vetoes).")
    

#command functionality
@client.event
async def on_message(msg):
    #check to see if bot sent this message
    if (msg.author == client.user):
        return

    msgtext = msg.content
    channel = msg.channel
    hobchannel = get_channel(client.get_all_channels(), HOBBIES_CHANNEL_NAME)

    #only run in hobbies channel
    if (channel != hobchannel):
        return

    #commands
    if (msgtext == "!listall"):
        await upload_file(channel, PATH_ALL)
    if (msgtext == "!listlater"):
        await upload_file(channel, PATH_LATER)
    if (msgtext == "!listtodo"):
        await upload_file(channel, PATH_TODO)
    if (msgtext == "!listvetoed"):
        await upload_file(channel, PATH_VETOED)
    if (msgtext == "!newhobby"):
        await new_hobby(hobchannel)
    if (msgtext == "!currenthobby"):
        await current_hobby(hobchannel)

    #testing
    if (msgtext == "greetings hobbot"):
        await hobchannel.send(f"greetings {msg.author.mention}")
    if (msgtext == "hobbot, shut down"):
        await hobchannel.send("goodbye world")
        await client.logout()
    if (msgtext == "hobbot, initiate test"):
        await hobchannel.send("testing...")
        await hobchannel.send("hobbot, shut down")

#start or something?
client.run(TOKEN)