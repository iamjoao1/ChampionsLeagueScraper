import requests
import re
from bs4 import BeautifulSoup as soup
import json
import brotli


#header
headers={
    'authority':'data.len.eu',
    'method':'GET',
    'path':'/export/PNChampionsLeague/ASM1A011FTCJSP/STA_ASM1A011FTCJSP9078.JSON?x=2085',
    'scheme':'https',
    'accept':'application/json, text/javascript, */*; q=0.01',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'classe-control':'no-cache',
    'cookie':'ASPSESSIONIDSQAQQCBA=HPHFAJJACODNGPKMJMFNHEID',
    'pragma':'no-cache',
    'referer':'https://data.len.eu/indexCL_web_fsWordPress.php?c=ASM&g=1&t=A01&gr=1&s1=FTC&s2=JSP&st=2',
    'sec-ch-ua':'" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile':'?0',
    'sec-ch-ua-platform':'"Windows"',
    'sec-fetch-dest':'empty',
    'sec-fetch-mode':'cors',
    'sec-fetch-site':'same-origin',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'x-requested-with':'XMLHttpRequest'}




#===============#get dates for the games#================#
print('===========requesting for the dates of games===========')
print('===========separating the rounds=======================')
response = requests.get('http://data.len.eu/calendar.php',headers=headers).content

#parse response
soup = soup(response,'lxml')
#find script
findScript = str(soup("script"))

dates_and_rounds = []
regex = 'arrGiorniGara.push\("(.*)"'
'''
#==================================================#

#get dates for qualification round 1
first_index = findScript.find('// 001')
second_index = findScript.find('// 002')

#use regex to find dates within the space of round 1
slice_p= findScript[first_index:second_index]
qualification_round_1 =[]
placeholder_list = re.findall(regex, slice_p)

#format dates 
for date in placeholder_list:
    qualification_round_1.append(date.replace("/",""))

#format--> [round game date info(list), name of round]
dates_and_rounds.append([qualification_round_1,'qualification_round_1'])
#==================================================#
#get dates for qualification round 2
first_index = findScript.find('// 002')
second_index = findScript.find('// 003')

#use regex to find dates within the space of round 1
slice_p= findScript[first_index:second_index]
qualification_round_2 =[]
placeholder_list = re.findall(regex, slice_p)

#format dates 
for date in placeholder_list:
    qualification_round_2.append(date.replace("/",""))

#format--> [round game date info(list), name of round]
dates_and_rounds.append(([qualification_round_2,'qualification_round_2']))
#==================================================#
#get dates for qualification round 3
first_index = findScript.find('// 003')
second_index = findScript.find('// A01')

#use regex to find dates within the space of round 1
slice_p= findScript[first_index:second_index]
qualification_round_3 =[]
placeholder_list = re.findall(regex, slice_p)

#format dates 
for date in placeholder_list:
    qualification_round_3.append(date.replace("/",""))

#format--> [round game date info(list), name of round]
dates_and_rounds.append(([qualification_round_3,'qualification_round_3']))
#==================================================#
'''
#get dates for the preliminary round
first_index = findScript.find('// A01')
second_index = findScript.find('// Final 8')

#use regex to find dates within the space of round 1
slice_p= findScript[first_index:second_index]
preliminary_round =[]
placeholder_list = re.findall(regex, slice_p)

#format dates 
for date in placeholder_list:
    preliminary_round.append(date.replace("/",""))

#format--> [round game date info(list), name of round]
dates_and_rounds.append(([preliminary_round,'preliminary_round']))



#===============#get games for each date#================#
print('===========creating and requesting url for the games for each date=======================')
date_game_urls = []
for round_ in dates_and_rounds:
    #for game date in list of game dates
    for game_date in round_[0]:
        #format --> [url for a game in that round, round name]
        date_game_urls.append(["https://data.len.eu/export/PNChampionsLeague/SCH_"+ game_date +".JSON?x=1",round_[1]])
    

game_parameters=[]
for date_url in date_game_urls:
    #date_url[0] = url of games by date
    response = requests.get(date_url[0],headers=headers).text
    
    #decode json response
    json_response = json.loads(response)
    for parameter in json_response['e']:
        game_parameters.append({
            #date_url[1] = name or round. Format ==> {url_parameter:[parameters_for_each_game,game's round]}
            'c':[parameter["c0"],date_url[1]],
            'g':[parameter["c1"],date_url[1]],
            't':[parameter["c2"],date_url[1]],
            'gr':[parameter["c3"],date_url[1]],
            's1':[parameter["c4"],date_url[1]],
            's2':[parameter["c5"],date_url[1]],
            'st':[parameter["st"],date_url[1]],
            'cp':[parameter["cp"],date_url[1]],
            })

#===============#get all the info on each game#+==================#
print('===========using created urls to request each games info=======================')      
games_stats_final=[]
for game in game_parameters:
    print('------------loading a game using game parameters-------------------')
    # request for the games data --> data.len.eu/indexCL_web_fsWordPress.php?c=ASM&g=1&t=A01&gr=1&s1=BAR&s2=RAD&st=0
    #format --> request for the games data but modified
    squashed_parameters = game['c'][0]+ game['g'][0]+ game['t'][0]+ game['gr'][0]+ game['s1'][0]+ game['s2'][0]
    url="https://data.len.eu/export/PNChampionsLeague/"+squashed_parameters+"/STA_"+squashed_parameters + game['cp'][0]+".JSON?x=1"
    response = requests.get(url,headers=headers).text
    #parse and get important info on each request -- if it cant parse it, that means it found an unsatisfactory answer
    try:
        json_response = json.loads(response)
    except:
        #format --> [round name,[team_one_name, 0-->no stats info],[team_two_name, 0-->no stats info]]
        games_stats_final.append([game['c'][1],[json_response['d1_en'],0],[json_response['d1_en'],0]] )
        continue

    #name of round of current game whose stats are being recorded
    round_name = game['c'][1];
    
    #get_team_names
    team_one_name=json_response['d1_en']
    team_two_name=json_response['d2_en']
    
    #initialize the team one list
    team_one_stats= [["Player"],["TOTAL"],["%"],["A"],["C"],["X"],["6M"],["PS"],["CA"],["PSO"],["AS"],["TF"],["ST"],["BL"],["SP"],["20C"],["20F"],["2EX"],["P"],["EX"],["4EX"]]
    for player in json_response['s1_s']:
        print('------------loading player '+ player['n']+" "+player['c'] +' that plays for'+ team_one_name +'-------------------')
        #add the player name
        team_one_stats[0].append(player['n']+" "+player['c'])
        #add the player stats
        for n,stat in enumerate(player['s']):
            team_one_stats[n+1].append(stat)

    team_one_stats[0].append('Total')
    #add total to team one list
    #for each value in the stats
    for n,stat in enumerate(json_response['s1_t']):
        team_one_stats[n+1].append(stat)
        
                     


    #initialize the team two list
    team_two_stats= [["Player"],["TOTAL"],["%"],["A"],["C"],["X"],["6M"],["PS"],["CA"],["PSO"],["AS"],["TF"],["ST"],["BL"],["SP"],["20C"],["20F"],["2EX"],["P"],["EX"],["4EX"]]
    for player in json_response['s2_s']:
        print('------------loading player '+ player['n']+" "+player['c'] +' that plays for '+ team_two_name +'-------------------')
        #add the player name
        team_two_stats[0].append(player['n']+" "+player['c'])
        #add the player stats
        for n,stat in enumerate(player['s']):
            team_two_stats[n+1].append(stat)
   
    team_two_stats[0].append('Total')
    #add total to team one list
    #for each value in the stats
    for n,stat in enumerate(json_response['s2_t']):
        team_two_stats[n+1].append(stat)
       
                   
    #add stats to final_list
    print('------------saved the game between '+team_one_name + team_two_name +' in '+round_name+' -------------------')
    #format-->[round name, [team name, team stats],[opp team name, opp team stats]] --> each list represents a game           
    games_stats_final.append([round_name,[team_one_name,team_one_stats],[team_two_name,team_two_stats]])


        
    
    
    
