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
async def on_raw_reaction_add(reaction_event):
    if (reaction_event.message_id == 732503159846600785) & (reaction_event.emoji.name == 'bigbrain'):
        guild_item = discord.utils.find(lambda g: g.id == reaction_event.guild_id, client.guilds)

        member = discord.utils.find(lambda m: m.id == reaction_event.user_id, guild_item.members)
        role = discord.utils.get(guild_item.roles, name='Debater')
        await member.add_roles(role)

@client.event
async def on_raw_reaction_remove(reaction_event):
    if (reaction_event.message_id == 732503159846600785) & (reaction_event.emoji.name == 'bigbrain'):
        guild_item = discord.utils.find(lambda g: g.id == reaction_event.guild_id, client.guilds)

        member = discord.utils.find(lambda m: m.id == reaction_event.user_id, guild_item.members)
        role = discord.utils.get(guild_item.roles, name='Debater')
        await member.remove_roles(role)

client.run(TOKEN)