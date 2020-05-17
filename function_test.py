import datetime
import json
import os
import re
from collections import Counter

os.chdir(os.path.dirname(__file__))


class VoteCountObj:
    def __init__(self, VoteTitle='', VoteDict = dict(), VoteDuration=60):
        self.VoteTitle = VoteTitle
        self.VoteDict = VoteDict
        self.VoteDuration = VoteDuration


VoteCounter = VoteCountObj('Wie was de Fox?', VoteDuration=30)
VoteCounter.VoteDict['Jim Morrison'] = 'Aaron'
VoteCounter.VoteDict['Aaron'] = 'Flippy'
VoteCounter.VoteDict['Serrr'] = 'Flippy'

print(list(VoteCounter.VoteDict.values()))

def print_result_of_vote(VoteCounter):
    CounterOutput = Counter(VoteCounter.VoteDict.values()).most_common()
    strToPost = 'Voting result for "{}"\n'.format(VoteCounter.VoteTitle)
    for votes in CounterOutput:
        strToPost = strToPost + '{}: {}\n'.format(votes[0],str(votes[1]))

    return strToPost