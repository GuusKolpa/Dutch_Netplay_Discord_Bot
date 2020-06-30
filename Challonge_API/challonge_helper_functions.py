import os,sys,inspect
from bot_resources import standard_messages
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


def post_netplay_tournament(create_tournament_json_data):
    file = open('challonge_config.yml', 'r')
    cfg = yaml.load(file, Loader=yaml.FullLoader)
    tournament_number = cfg['automate_netplay_tournament']['last_iteration']+1
    create_tournament_url = 'https://api.challonge.com/v1/tournaments{}.json'
    jsonResponse = requests.post(url = create_tournament_url.format(''), data = create_tournament_json_data).json()
    newEntry = False
    print(jsonResponse)
    if not 'errors' in jsonResponse:
        print('Tournament created')
        sign_up_link = jsonResponse['tournament']['sign_up_url']
        resultMessage = standard_messages.netplay_tournament_start.format(sign_up_link, tournament_number)
        newEntry = True
        return resultMessage, newEntry
    else:
        if 'URL is already taken' in jsonResponse['errors']:
            jsonResponse = requests.put(url = create_tournament_url.format("/" + create_tournament_json_data['tournament[url]']), data = create_tournament_json_data).json()
            sign_up_link = jsonResponse['tournament']['sign_up_url']
            print('Tournament exists, updating tournament')
            resultMessage = standard_messages.netplay_tournament_start.format(sign_up_link, tournament_number)
            cfg['automate_netplay_tournament']['netplay_tournament'] = tournament_number
            with open('challonge_config.yml', "w") as f:
                yaml.dump(cfg, f)
            return resultMessage, newEntry
        else:
            print(jsonResponse['errors'])
            resultMessage = 'Problem with creating/updating tournament, please contact bot owner'
            return resultMessage, newEntry