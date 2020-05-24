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
import datetime
import asyncio
from functions import discord_bot_helper_functions as helper
from resources import standard_messages

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

last_netplay_tournament_sent = cfg['automate_netplay_tournament']['last_message_time']
def next_tuesday(input_date):
    def next_weekday(d):
        days_ahead = 1 - d.weekday()
        if days_ahead <= 0: # Target day already happened this week
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)
    next_tuesday = next_weekday(input_date)
    next_netplaytournament_send_time = datetime.datetime(next_tuesday.year, next_tuesday.month, next_tuesday.day, 16, 0, 0)
    return next_netplaytournament_send_time

when = next_tuesday(last_netplay_tournament_sent)
print(when)
# client.loop.create_task(helper.automated_netplay_tournament(client, cfg))
# client.run(TOKEN)
