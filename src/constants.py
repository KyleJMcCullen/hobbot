"""
constants used across modules
"""

from dotenv import load_dotenv
import os


load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
#CURSENT_ID = os.getenv('CURSENT_ID')
HOBBIES_CHANNEL_ID = os.getenv('HOBBIES_CHANNEL_ID')
HOBBIES_CHANNEL_NAME = "hobbies"
JSON_NO_HOBBY = "NONE"
NUM_VETOES_TO_SKIP = 3

PATH_ALL = "../files/all.txt"
PATH_COMPLETE = "../files/complete.json"
PATH_CURRENT = "../files/current.json"
PATH_LATER = "../files/later.json"
PATH_TODO = "../files/todo.txt"
PATH_VETOED = "../files/vetoed.json"