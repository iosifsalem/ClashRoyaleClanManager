# Clash Royale Clan Manager
# computes promotion/demotion/kick/warning lists, average war rank, and weekly war champ according to clan wars II statistics
# uses data from Supercell's Clash Royale API

import json
import requests
import statistics

def data_fetcher(clan_tag, token, category):
    # fetches data from API for a given category
    # categories: currentriverrace, riverracelog, warlog, members, members?limit=50, empty input for clan info etc
    
    myheaders = {} 
    myheaders['Accept'] = 'application/json'
    myheaders['authorization'] = 'Bearer '+token

    clan_tag_for_url = '%23' + clan_tag[1:]  # replace # with %23 for the http get request        
    url = "https://api.clashroyale.com/v1/clans/" + clan_tag_for_url + '/' + category

    response = requests.request("GET", url, headers=myheaders)

    return response.json()


def ClashRoyaleClanManager(clan_tag, token, data_fetched):
    # computes promotion/demotion/kick/warning lists, average war rank, and weekly war champ
    
    # fetch and log data
    if data_fetched:
        with open('logs/members.json', 'r') as outfile:
            members = json.load(outfile)  
            
        with open('logs/riverracelog.json', 'r') as outfile:
            riverracelog = json.load(outfile)  
        
    else:
        print('Fetching members data...')
        members = data_fetcher(clan_tag, token, 'members') 
        with open('logs/members.json', 'w') as outfile:
            json.dump(members, outfile)  

        print('Fetching riverracelog data...')
        riverracelog = data_fetcher(clan_tag, token, 'riverracelog') 
        with open('logs/riverracelog.json', 'w') as outfile:
            json.dump(riverracelog, outfile)  
    
    race_indices = [f"{war_week['seasonId']}:{war_week['sectionIndex']}" for war_week in riverracelog['items']]
    last_race = str(max(race_indices))
    race_indices.remove(last_race)
    second_last_race = str(max(race_indices))
    
    # tags of current members
    member_tags = [member['tag'] for member in members['items']]
            
    # init dictionary to store the clan log 
    clan_log = {}
    
    clan_log['ranks'] = []

    # init fame     
    for member in members['items']:
        clan_log[member['tag']] = {'name':member['name'], 'role':member['role'], 'fame':{}}
    
    name_to_tag = {clan_log[key]['name']:key for key in clan_log if key != 'ranks'}
    
    # create clan history 
    for war_week in riverracelog['items']:
        # each war week is marked uniqely with "seasonId:sectionIndex"
        week_id = f"{war_week['seasonId']}:{war_week['sectionIndex']}"
        
        # locate clan entry 
        for entry in war_week['standings']:
            if entry['clan']['tag'] == clan_tag:
                clan_data = entry
        
        # add week data to clan_log
        for member in clan_data['clan']['participants']:
            if member['tag'] in member_tags:
                clan_log[member['tag']]['fame'][week_id] = member['fame']

        clan_log['ranks'].append(clan_data['rank'])

    print(f"Average war rank: {statistics.mean(clan_log['ranks'])}")

    # compute week champ
    week_fame = [(clan_log[key]['name'], clan_log[key]['fame'][last_race]) for key in clan_log if key != 'ranks' and last_race in clan_log[key]['fame']]
    week_fame.sort(key = lambda x: x[1])
    week_champ = week_fame.pop()
        
    # status update lists
    last_two_weeks_fame = [(clan_log[key]['name'], clan_log[key]['role'], clan_log[key]['fame'][last_race], clan_log[key]['fame'][second_last_race]) for key in clan_log if key != 'ranks' and last_race in clan_log[key]['fame'] and second_last_race in clan_log[key]['fame']]    
    kick_list = []
    demotion_list = []
    promotion_list = []
    warning_list = []

    for item in last_two_weeks_fame:
        role = item[1]
        last_week_fame = item[2]
        second_last_week_fame = item[3]
        
        # promotion rule: two consecutive weeks of at least 1600 fame in war
        if last_week_fame > 1600 and second_last_week_fame > 1600 and role == 'member':
            promotion_list.append(item)

        # warning rule: less than losing all attacks in 3/4 days in the last war 
        if last_week_fame < 1200:
            warning_list.append(item)

        # demotion rule (elders): less than 1600 for two consecutive weeks 
        if last_week_fame < 1600 and second_last_week_fame < 1600 and role == 'elder':
            demotion_list.append(item)
            
        # kick rule: total score for two consecutive weeks is less than 2800 
        # thresshold can be achieved by losing all attacks in 3/4 (1200) and 4/4 (1600) days 
        if last_week_fame + second_last_week_fame < 2800 and role == 'member':
            kick_list.append(item)       

    print('\nfull war history of members in kick list:')
    for item in kick_list:
        name = item[0]
        print(f"{name}: {clan_log[name_to_tag[name]]['fame']}")      
    print("\n")
    
    with open("logs/clan-log.json", "w") as outfile:
        json.dump(clan_log, outfile)
    
    return week_champ, promotion_list, demotion_list, kick_list, warning_list
    

## customizations: edit only this part of the code to adapt it to your clan

clan_tag = input("insert clan tag (starting with #): ")

# key created via supercell's CR api
token = input("insert token from Supercell's Clash Royale API: ")

# set to True to compute the output from the local files 
data_fetched = False

week_champ, promotion_list, demotion_list, kick_list, warning_list = ClashRoyaleClanManager(clan_tag, token, data_fetched)

print(f"Week champ: {week_champ} \nPromote: {promotion_list} \nDemote: {demotion_list} \nKick: {kick_list} \nwarning list: {warning_list}")