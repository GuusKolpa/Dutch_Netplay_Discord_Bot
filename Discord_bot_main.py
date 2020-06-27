# bot.py

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from dotenv import load_dotenv
import glob, json, asyncio, yaml, discord

from functions import discord_bot_helper_functions as helper

li = []

filename = "./bot_resources/Dutch_Melee_Discord_Post_History.csv"
frame = pd.read_csv(filename, index_col=None,
                    header=0, parse_dates=['DateCol'])


with open('./bot_resources/help_doc.json') as handle:
    help_dict = json.loads(handle.read())
with open('./bot_resources/role_assignments.json') as handle:
    roles_dict = json.loads(handle.read())

file = open('config.yml', 'r')
cfg = yaml.load(file, Loader=yaml.FullLoader)

client = discord.Client()

# Make sure to put the DISCORD_TOKEN environment variable with your appropriate token.
TOKEN = os.getenv('DISCORD_TOKEN')

class VoteCheck:
    def __init__(self, ActiveVote=False):
        self.ActiveVote = ActiveVote

    def __repr__(self):
        return str(self.ActiveVote)

    def __str__(self):
        return str(self.ActiveVote)

class VoteCountObj:
    def __init__(self, VoteTitle='', VoteDict = dict(), VoteDuration=60, VoteTimeLeft=60):
        self.VoteTitle = VoteTitle
        self.VoteDict = VoteDict
        self.VoteDuration = VoteDuration
        self.VoteTimeLeft = VoteTimeLeft


VoteChecker = VoteCheck(False)
VoteCounter = VoteCountObj('init', VoteDict=dict(), VoteDuration=60, VoteTimeLeft=60)

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
    if  (message.channel.id == cfg['channel_ids']['bot_commands']) &(messageContent[0] == '!'):
        args = messageContent.split()[1:]
        command = messageContent.split()[0].lower()

        if command == '!help':
            # Returns the doc for a specific command #
            returnMessage = helper.retrieve_help_command(args, help_dict)
            await message.channel.send(returnMessage)

        elif command == '!generate':
            # Generates a random quote #
            returnMessage = helper.generate_quote(frame, args)
            await message.channel.send(returnMessage)

        elif command == '!image':
            # Generates a random image #
            returnMessage = helper.generate_image(frame, args)
            await message.channel.send(returnMessage)

        elif command == "!carol":
            # Generates a random Smasher's Carol quote #
            carol_file = "./bot_resources/smash_carols_curated.csv"
            carol_quotes = pd.read_csv(carol_file, index_col=None,
                                header=0)
            carol_quotes_curated = carol_quotes[carol_quotes["Quality"]==1]
            returnMessage = carol_quotes_curated.sample(1).reset_index()["Sentence"][0]
            await message.channel.send(returnMessage)

        elif command == '!start_vote':
            # Must at least be able to manage messages to start a vote count
            if not any([role.permissions.manage_messages for role in message.author.roles]):
                await message.channel.send('Unauthorized command')
                return

            if VoteChecker.ActiveVote == True:  # Check if another vote is already occurring
                await message.channel.send('Another vote is already underway')
                return

            vote_title = helper.retrieve_unnamed_argument(args, '')
            vote_duration = int(helper.retrieve_named_argument(args, 'time', 60))
            VoteCounter.VoteTitle, VoteCounter.VoteDict, VoteCounter.VoteDuration = (vote_title, dict(), vote_duration)
            messageSent = await message.channel.send('Now counting votes for "{}" ({} seconds remaining)\nHow to vote:\n!vote YOUR VOTE HERE'.format(vote_title, vote_duration))

            VoteChecker.ActiveVote = True
            for i in range(1, vote_duration):
                if VoteChecker.ActiveVote == True:
                    await asyncio.sleep(1)
                    await messageSent.edit(content = 'Now counting votes for "{}" ({} seconds remaining)\nHow to vote:\n!vote YOUR VOTE HERE'.format(vote_title, vote_duration-i))
                    VoteCounter.VoteTimeLeft = vote_duration-i
                else:
                    break

            VoteCounter.VoteTimeLeft = 0
            await messageSent.edit(content = 'Voting over for "{}"'.format(vote_title))
            if VoteChecker.ActiveVote == True:
                VoteChecker.ActiveVote = False
                helper.write_voting_results_to_local(VoteCounter)
                await message.channel.send(helper.print_result_of_vote(VoteCounter))
            

        elif command == '!cancel_vote':
            # Must at least be able to manage messages to start a vote count
            if not any([role.permissions.manage_messages for role in message.author.roles]):
                return
            if VoteChecker.ActiveVote == True:
                VoteChecker.ActiveVote = False
                await message.channel.send('Vote canceled for "{}"'.format(VoteCounter.VoteTitle))
                helper.write_voting_results_to_local(VoteCounter)
                await message.channel.send(helper.print_result_of_vote(VoteCounter))

        elif command == '!current_vote':
            # Returns the current active vote
            if VoteChecker.ActiveVote == False:
                returnMessage = 'No active vote'
            else:
                returnMessage = 'Current vote: "{}"\n{} seconds remaining'.format(VoteCounter.VoteTitle, VoteCounter.VoteTimeLeft)
            await message.channel.send(returnMessage)

        elif command == '!vote':
            # Counts a vote. Only works if the start_vote command has set the VoteChecker.ActiveVote property to TRUE # 
            if VoteChecker.ActiveVote == True:
                
                vote_name = message.author.name
                vote_for = helper.retrieve_unnamed_argument(args, None).capitalize()
                if vote_for == None:
                    return
                VoteCounter.VoteDict[vote_name] = vote_for
                await message.add_reaction(u"\U0001F44D")
            else:
                await message.channel.send('No active vote')

        elif command == '!botkill':
            if any([role.permissions.kick_members for role in message.author.roles]):
                await message.channel.send('Until next time! \U0001F44B')
                await client.close()
            else:
                await message.add_reaction(u"\U0001F621")
        else:
            # If command does not exist, mention it #
            returnMessage = 'Command {} not found'.format(command)
            await message.channel.send(returnMessage)



client.loop.create_task(helper.automated_netplay_tournament(client, cfg))
client.run(TOKEN)
