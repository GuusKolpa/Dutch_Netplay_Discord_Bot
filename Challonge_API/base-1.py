import os,sys,inspect
import requests, pytz, yaml, json, datetime

def create_tournament_parameters():
    file = open('challonge_config.yml', 'r')
    cfg = yaml.load(file, Loader=yaml.FullLoader)

    with open('./Challonge_API/create_tournament.json') as json_file:
        data = json.load(json_file)
    CHALLONGE_API_KEY = os.getenv('CHALLONGE_TOKEN')
    tournament_number = cfg['automate_netplay_tournament']['last_iteration']+1

    NL_timezone = pytz.timezone('Europe/Amsterdam')
    start_time = NL_timezone.localize(datetime.datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)).__str__()
    data['api_key'] = CHALLONGE_API_KEY
    data['tournament[name]'] = data['tournament[name]'].format(tournament_number)
    data['tournament[url]'] = data['tournament[url]'].format(tournament_number)
    data['tournament[start_at]'] = start_time
    return data

print(create_tournament_parameters())

file = open('challonge_config.yml', 'r')
cfg = yaml.load(file, Loader=yaml.FullLoader)
tournament_number = cfg['automate_netplay_tournament']['last_iteration']+1
create_tournament_url = 'https://api.challonge.com/v1/tournaments{}.json'
jsonResponse = requests.post(url = create_tournament_url.format(''), data = create_tournament_parameters())
print(create_tournament_url.format(''), create_tournament_parameters())
print(create_tournament_url.format(''))