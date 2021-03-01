# hobbot.py
import os
import re

import discord
import json
import wikipedia

from constants import GUILD
from constants import HOBBIES_CHANNEL_ID
from constants import HOBBIES_CHANNEL_NAME
from constants import JSON_NO_HOBBY
from constants import PATH_ALL
from constants import PATH_COMPLETE
from constants import PATH_CURRENT
from constants import PATH_LATER
from constants import PATH_TODO
from constants import PATH_VETOED
from constants import TOKEN
import commands as cmd
import infogetters as info

#hobbies channel
hobchannel = None

client = discord.Client()

# TODO
# - retrieve info about a completed hobby
# - pull from "later" bin
# - make list{file} functions print out up to 2000 chars before uploading file


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


#command functionality
@client.event
async def on_message(msg):
    #check to see if bot sent this message
    if (msg.author == client.user):
        return

    msgtext = msg.content
    channel = msg.channel
    
    global hobchannel

    hobchannel = get_channel(client.get_all_channels(), HOBBIES_CHANNEL_NAME)

    if (hobchannel == None):
        print ("hobchannel is None")

    #only run in hobbies channel
    if (channel != hobchannel):
        return

    #commands
    if (msgtext == "!help"):
        await cmd.list_commands(hobchannel)
    elif (msgtext == "!listall"):
        await cmd.upload_file_to_channel(PATH_ALL, hobchannel)
    elif (msgtext == "!listlater"):
        await cmd.upload_file_to_channel(PATH_LATER, hobchannel)
    elif (msgtext == "!listtodo"):
        await cmd.upload_file_to_channel(PATH_TODO, hobchannel)
    elif (msgtext == "!listvetoed"):
        await cmd.upload_file_to_channel(PATH_VETOED, hobchannel)
    elif (msgtext == "!newhobby"):
        await cmd.new_hobby(hobchannel)
    elif (msgtext in ["!currenthobby", "!current"]):
        await cmd.print_current_hobby(hobchannel)
    elif (msgtext == "!summary"):
        await cmd.print_summary(hobchannel)
    elif (msgtext == "!complete"):
        await cmd.mark_current_as_complete(hobchannel)
    elif (msgtext == "!veto"):
        await cmd.handle_veto(msg.author, hobchannel)
    elif (msgtext == "!later"):
        await cmd.move_current_to_later(hobchannel)
    elif (str.startswith(msgtext, "!addnote ")):
        await cmd.add_note_to_current(msgtext[9:], msg.author.name, hobchannel)
    elif (str.startswith(msgtext, "!pickhobby ")):
        await cmd.pick_hobby_from_later(msgtext[11:], hobchannel)

    #testing
    elif (msgtext == "greetings hobbot" or msgtext == "good morning hobbot" or msgtext == "good afternoon hobbot"):
        await hobchannel.send(f"greetings {msg.author.mention}")
    elif (msgtext == "hobbot, shut down" or msgtext == "goodbye hobbot"):
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