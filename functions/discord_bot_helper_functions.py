import os,sys,inspect
from os import listdir
from os.path import isfile, join
from binance.client import Client as biClient

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

api_key = os.getenv('binance_api_key')
api_secret = os.getenv('binance_api_secret')

binance_client = biClient(api_key, api_secret)

import Challonge_API.challonge_helper_functions as challonge_helper
from bot_resources import standard_messages
from collections import Counter
import datetime, re, json, yaml, asyncio, discord



class CustomError(Exception):
    pass

def on_ready():
    print("We have logged in")


def generate_quote(generating_frame, args):
    '''Randomly generate a image. Input is the full discord dataframe and an argument list. 

    Currently, the arguments are:
    DiscordID (must be first argument, no argument check)
    Keyword (argument -keyword)
    Post length (argument -postLength, default = 50)
    '''

    DiscordIDInput = retrieve_unnamed_argument(args)
    ContainsKeyword = retrieve_named_argument(args, 'keyword')
    CharacterLimit = int(retrieve_named_argument(args, 'postLength', '50'))

    FilterOutPersonIDs = []
    RandomFrame = generating_frame[generating_frame["PostLength"]
                                   > CharacterLimit]
    RandomFrame = RandomFrame[~RandomFrame['Author'].isin(FilterOutPersonIDs)]
    if DiscordIDInput == None:
        pass
    else:
        RandomFrame = RandomFrame[RandomFrame["Author"].str.contains(
            DiscordIDInput, case=False, regex=False)]
    if ContainsKeyword == None:
        pass
    else:
        RandomFrame = RandomFrame[RandomFrame["Content"].str.contains(
            ContainsKeyword, case=False, regex=False)]

    if not RandomFrame.empty:


        SingleRandom = RandomFrame.sample(1).reset_index()

        SingleRandomContent = SingleRandom["Content"][0]
        SingleRandomAuthor = SingleRandom["Author"][0][:-5]
        SingleRandomDate = SingleRandom["DateCol"].dt.strftime('%B %Y @ %H:%M')[
            0]
        returnMessage = '"{}" - {}, {}'.format(
            SingleRandomContent, SingleRandomAuthor, SingleRandomDate)
    else:
        returnMessage = 'No suitable messages found for user with ID containing "{}"'.format(
            DiscordIDInput)
    return returnMessage


def generate_image(generating_frame, args):
    """Randomly generate an image. Input is the full discord dataframe and an argument list. Currently, the only argument is the user.
    """
    RandomFrame = generating_frame.dropna(subset=["Attachments"])

    DiscordIDInput = retrieve_unnamed_argument(args)
    FilterOutPersonIDs = []
    RandomFrame = RandomFrame[~RandomFrame['Author'].isin(FilterOutPersonIDs)]
    if DiscordIDInput == None:
        pass
    else:
        RandomFrame = RandomFrame[RandomFrame["Author"].str.contains(
            DiscordIDInput, case=False, regex=False)]
    if not RandomFrame.empty:
        SingleRandom = RandomFrame.sample(1).reset_index()

        SingleRandomAttachment = SingleRandom["Attachments"][0]
        SingleRandomAuthor = SingleRandom["Author"][0][:-5]
        SingleRandomDate = SingleRandom["DateCol"].dt.strftime('%B %Y @ %H:%M')[
            0]
        returnMessage = '{} - {}, {}'.format(
            SingleRandomAttachment, SingleRandomAuthor, SingleRandomDate)
    else:
        returnMessage = 'No suitable attachments found for user with ID containing "{}"'.format(
            DiscordIDInput)

    return returnMessage


def retrieve_named_argument(args, argument_name, default_value=None):
    """Retrieves a named argument (prefixed with -)
    """
    argument_value = default_value
    argument_val_list = []
    for i, arg in enumerate(args):
        if (arg[0] == '-') & (arg[1:] == argument_name):
            for following_args in args[i+1:]:
                if following_args[0] == '-':
                    break
                else:
                    argument_val_list.append(following_args)
            argument_value = ' '.join(argument_val_list)
            break
    return argument_value


def retrieve_unnamed_argument(args, default_value=None):
    """Retrieves the first argument provided by concatenating each following separate line. When an argument starts with '-', the first argument is done.
    """
    argument_value = default_value
    argument_val_list = []
    NameCheck = True
    for arg in args:
        if arg[0] == '-':
            NameCheck = False
            break
        if NameCheck:
            argument_val_list.append(arg)
    if argument_val_list:
        argument_value = ' '.join(argument_val_list)
    
    return argument_value


def retrieve_help_command(args, help_dict):
    try:
        returnMessage = help_dict[args[0].lower()]
    except:
        if not args:
            returnMessage = help_dict['help']
        else:
            returnMessage = "Command {} not found".format(args[0])
    return returnMessage

def write_voting_results_to_local(VoteCounterObject):
    formattedVoteTitle = VoteCounterObject.VoteTitle.lower().replace(' ', '_')
    formattedVoteTitle = re.sub(r'[\/:*?"<>|]', '', formattedVoteTitle)
    timeNowFormatted = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    with open("./voting_results/{}-{}.json".format(timeNowFormatted, formattedVoteTitle), 'w') as outfile:
        json.dump(VoteCounterObject.__dict__, outfile)


def print_result_of_vote(VoteCounter):
    if not bool(VoteCounter.VoteDict):
        return 'No votes recorded'
    else:
        CounterOutput = Counter(VoteCounter.VoteDict.values()).most_common()
        strToPost = 'Voting result for "{}"\n'.format(VoteCounter.VoteTitle)
        for votes in CounterOutput:
            strToPost = strToPost + '{}: {}\n'.format(votes[0],str(votes[1]))
        return strToPost

def update_last_netplay_tournament_config(messageSent, newEntry, config):
    """Update the config.yml file to have the most recent tournament update.
    """
    config['automate_netplay_tournament']['last_message_id'] = messageSent.id
    config['automate_netplay_tournament']['last_message_time'] = messageSent.created_at
    if newEntry:
        config['automate_netplay_tournament']['last_iteration'] = config['automate_netplay_tournament']['last_iteration']+1
    with open('challonge_config.yml', "w") as f:
        yaml.dump(config, f)

def retrieve_channel(Client, UseNameOrId, Identifier):
    """Returns a channel object based or either name or Id.
    """
    text_channel_object = None
    for channel in Client.get_all_channels():
        if UseNameOrId == 'id':
            if channel.id == Identifier:
                text_channel_object = channel
                break
        else:
            if channel.name == Identifier:
                text_channel_object = channel
                break
    return text_channel_object

async def automated_netplay_tournament(client, config):
    """Automates the creation of the Dutch Netplay Tournament Series. Each Tuesday at 13:00, a link is posted.
    """
    await asyncio.sleep(5)
    while True:
        last_netplay_tournament_sent = config['automate_netplay_tournament']['last_message_time']
        when = next_tuesday(last_netplay_tournament_sent)
        print('Starting next netplay tournament at ', when)
        await discord.utils.sleep_until(when, result=None)
        with open('config.yml', 'r') as handle:
            netplayChannelId = yaml.load(handle, Loader=yaml.FullLoader)['channel_ids']['netplay_tournament']
            print(netplayChannelId)
        returnMessage, newEntry = challonge_helper.post_netplay_tournament(challonge_helper.create_tournament_parameters())
        channelToSend = client.get_channel(netplayChannelId)
        messageSent = await channelToSend.send(returnMessage)
        update_last_netplay_tournament_config(messageSent, newEntry, config)
        print('Netplay tournament created at {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

def next_tuesday(input_date):
    """Returns the date that the next netplay tournament should be organised, based on the time the last netplay tournament message was sent.
    """
    def next_weekday(d):
        days_ahead = 1 - d.weekday()
        if days_ahead <= 0: # Target day already happened this week
            days_ahead += 7
        return d + datetime.timedelta(days_ahead)
    next_tuesday = next_weekday(input_date)
    next_netplaytournament_send_time = datetime.datetime(next_tuesday.year, next_tuesday.month, next_tuesday.day, 11, 0, 0)
    return next_netplaytournament_send_time

def add_emoji(discord_client, config, emojiName):
    home_guild_item = discord.utils.get(discord_client.guilds, id=config['guild_ids']['home_guild'])
    emoji = discord.utils.get(home_guild_item.emojis, name=emojiName)
    return emoji

def get_all_characters():
    CharacterList = ['Fox', 'Falco', 'Marth', 'Sheik', 'Jigglypuff', 'CaptainFalcon', 'PrincessPeach', 'Pikachu', 'Yoshi', 'IceClimbers', 'Samus', 'DonkeyKong', 'DrMario', 'Mario', 'Luigi', 'Ganondorf', 'Link', 'YoungLink', 'Pichu', 'Mewtwo', 'MrGameWatch', 'Roy', 'Ness', 'PrincessZelda', 'Kirby', 'Bowser']
    return CharacterList

def return_funds(config):
    lastStonksCheck = datetime.datetime.now() - config["stonks"]["last_stonks_check"]
    if (lastStonksCheck.days * 24 + lastStonksCheck.seconds/3600) < 1:
        return 'Calm down with the stonks-checking, I\'m still on cooldown <:armada:732312560057057310>'
    # get all symbol prices
    price_adausdt = float(binance_client.get_avg_price(symbol='ADAUSDT')['price'])
    community_fund_initial_ADA_total = config["stonks"]["community_fund_init_ADA"]
    community_fund_initial_ADA_price = config["stonks"]["community_fund_init_ADA_price"]
    community_fund_initial_usd = config["stonks"]["community_fund_init_USD"]
    current_usd = community_fund_initial_ADA_total*price_adausdt
    margin = current_usd/community_fund_initial_usd

    message_stonks = "**Current value of #stonks4Somnio community fund: ${current_usd} ({margin}x)**\nInitial fund: ${community_fund_initial_usd}\nCurrent ADA price: ${price_adausdt}\nStart ADA price: ${community_fund_initial_ADA_price}\nTotal ADA: {community_fund_initial_ADA_total}".format(current_usd=round(current_usd,2),
                                            margin = round(margin,2),
                                            community_fund_initial_usd=round(community_fund_initial_usd,2),
                                            community_fund_initial_ADA_price=round(community_fund_initial_ADA_price,3),
                                            price_adausdt=round(price_adausdt,3),
                                            community_fund_initial_ADA_total=round(community_fund_initial_ADA_total,2))
    config['stonks']['last_stonks_check'] = datetime.datetime.now()
    print(current_dir)
    with open('config.yml', "w") as f:
        yaml.dump(config, f)
    return message_stonks