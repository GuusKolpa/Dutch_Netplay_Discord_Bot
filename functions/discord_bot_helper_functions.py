import time
import os
import datetime
import re
import json
from collections import Counter


class CustomError(Exception):
    pass

def on_ready():
    print("We have logged in as")


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
            DiscordIDInput, case=False)]
    if ContainsKeyword == None:
        pass
    else:
        RandomFrame = RandomFrame[RandomFrame["Content"].str.contains(
            ContainsKeyword, case=False)]

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
            DiscordIDInput, case=False)]
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