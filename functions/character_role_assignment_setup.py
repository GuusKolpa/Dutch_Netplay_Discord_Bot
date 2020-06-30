# bot.py

import os,sys,inspect
from os import listdir
from os.path import isfile, join

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

import pandas as pd
from dotenv import load_dotenv
import glob, json, asyncio, yaml, discord

from functions import discord_bot_helper_functions as helper

li = []

with open('config.yml', 'r') as handle:
    cfg = yaml.load(handle, Loader=yaml.FullLoader)
client = discord.Client()

# Make sure to put the DISCORD_TOKEN environment variable with your appropriate token.
TOKEN = os.getenv('DISCORD_TOKEN')

@client.event  # event decorator/wrapper
async def on_ready():
    print(f"We have logged in as {client.user}")
    # await client.get_channel(
    #     cfg['channel_ids']['bot_commands']).send('Howdy! \U0001f920')


@client.event
async def on_message(message):
    messageContent = message.content
    # check against bot ID so we don't get a loop.
    if message.author.id == client.user.id:
        return
    if  (message.channel.id == cfg['channel_ids']['role-requests']):
        for characterName in helper.get_all_characters()[20:]:
            emoji = helper.add_emoji(client, cfg, characterName)
            await message.add_reaction(emoji)

client.run(TOKEN)