# bot.py
import pandas as pd
import matplotlib.pyplot as plt
import glob
from os.path import isfile, join
from os import listdir
import json
import asyncio
import logging
import threading
import time
from functions import discord_bot_helper_functions as helper
import os
import yaml

import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

file = open('config.yml', 'r')
cfg = yaml.load(file, Loader=yaml.FullLoader)

li = []

os.chdir(os.path.dirname(__file__))
client = discord.Client()
TOKEN = os.getenv('DISCORD_TOKEN')
@client.event  # event decorator/wrapper
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.channel.id == cfg['channel-ids']['guus-data']:
        channel = message.channel
        returnMessage = helper.retrieve_help_command(args, help_dict)
            await message.channel.send(returnMessage)
        # async for elem in channel.history().filter(predicate):
        #     print(elem.author)
        #     print(elem.content)
        print(channel.id)

def predicate(message):
    return not message.author.bot

print(cfg)
client.run(TOKEN)
