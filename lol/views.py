from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from lol.forms import SummonerForm
import requests, json
import pandas as pd
import time
import lol.api_config as config

# Set up code

key = config.api_key
current_season = '8'


def check_api_status():
    lol_status_url = 'https://na1.api.riotgames.com/lol/status/v3/shard-data?api_key='+key
    lol_status = requests.get(lol_status_url)
    if lol_status.status_code == 200:
        return True
    else:
        return False

riot_api_working = check_api_status()
if riot_api_working:
    #champion info/names
    url_champ_info = 'https://na1.api.riotgames.com/lol/static-data/v3/champions?locale=en_US&dataById=false&api_key=' + key
    championInfo = requests.get(url_champ_info)

    champ_dict = {}
    for champion in championInfo.json()['data']:
        champ_dict[championInfo.json()['data'][champion]['id']] = championInfo.json()['data'][champion]['name']

    # get current lol patch version
    version_url = 'https://na1.api.riotgames.com/lol/static-data/v3/versions?api_key=' + key
    versions = requests.get(version_url)
    if versions.status_code == 200:
        version = versions.json()[0]
    else:
        version = '7.23.1'  # manual

    def getChampSimpleName(champID):
        return champ_dict[champID].lower().replace(' ', '').replace('\'', '').replace('.', '')

    champ_ids = {}
    for champ_id in champ_dict:
        s = getChampSimpleName(champ_id)
        champ_ids[s] = champ_id


def error(request):
    if riot_api_working:
        return render(request, 'error.html', {'from': 'The Summoner Lookup hit a bug...sorry!'})
    else:
        return render(request, 'error.html', {'from': 'The Riot API is down.'})


def getSummonerChampLevel(tempChampID, summID):
    url = 'https://na1.api.riotgames.com/lol/champion-mastery/v3/champion-masteries/by-summoner/'+str(summID)+'/by-champion/'+str(tempChampID)+'?api_key='+key
    getChampExp = requests.get(url)
    if getChampExp.status_code == 200:
        #has experience
        #could also get championPoints and tokensEarned
        return getChampExp.json()['championLevel']
    else:
        return 0

# Create your views here


def summoner_landing(request):
    if request.method == 'POST':
        form = SummonerForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd.get('summoner_name')

            return HttpResponseRedirect('/summoner/'+name)
    else:
        form = SummonerForm()
        if riot_api_working is False:
            return render(request, 'error.html', {'from': 'The Riot API is down.'})
        return render(request, 'summoner_landing_page.html', {'form': form})


def summoner(request, sum_name):
    if request.method == 'POST':
        form = SummonerForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd.get('summoner_name')

            return HttpResponseRedirect('/summoner/'+name)
    else:
        if riot_api_working is False:
            return render(request, 'error.html', {'from': 'The Riot API is down.'})

        name = str(sum_name)
        form = SummonerForm(
            initial={'summoner_name': name}
        )
        plain_name = name.replace(' ', '')
        key = config.api_key #api key
        #name_requested_formatted = name.replace('+', '%20')
        url = 'https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/' + plain_name + '?api_key=' + key
        response = requests.get(url)
        if response.status_code == 404:
            return render(request, 'error.html', {'from': response.json()['status']['message']})
        elif response.status_code != 200:
            return render(request, 'error.html', {'from': response.json()['status']['message']})
        data = response.json()

        # get Summoner ID and name
        sumID = data['id']
        account_id = str(data['accountId'])
        icon_id = data['profileIconId']
        summoner_level = data['summonerLevel']
        sumID = str(sumID)
        icon_url = 'http://ddragon.leagueoflegends.com/cdn/'+version+'/img/profileicon/'+str(icon_id)+'.png'

        # Get summoner Rank
        # need to redo this
        url = 'https://na.api.pvp.net/api/lol/na/v2.5/league/by-summoner/' + sumID + '?api_key=' + key
        rank = requests.get(url)
        textRank = ''
        if rank.status_code == 200:
            for player in rank.json()[sumID][0]['entries']:
                if player['playerOrTeamId'] == sumID:
                    textRank = rank.json()[sumID][0]['tier'].capitalize() + ' ' + player['division'] + ' - ' + 'LP: ' + str(
                        player['leaguePoints'])
        else:
            textRank = 'Unranked'

        # Get Ranked Stats
        url = 'https://na.api.pvp.net/api/lol/na/v1.3/stats/by-summoner/' + sumID + '/ranked?season=SEASON2017&api_key=' + key
        rankedStats = requests.get(url)
        if rankedStats.status_code == 200:
            # get all champion ranked stats by champ id and put into DF
            personal_champ_ranked_stats = {}
            for champ in rankedStats.json()['champions']:
                if (champ['id'] == 0):
                    continue
                personal_champ_ranked_stats[champ['id']] = champ['stats']

            df_personal_champ_ranked_stats = pd.DataFrame(personal_champ_ranked_stats)
            df_personal_champ_ranked_stats = df_personal_champ_ranked_stats.T
            df_personal_champ_ranked_stats['KDA'] = (
                                                        df_personal_champ_ranked_stats.totalAssists + df_personal_champ_ranked_stats.totalChampionKills) / df_personal_champ_ranked_stats.totalDeathsPerSession
            df_personal_champ_ranked_stats[
                'winRatio'] = df_personal_champ_ranked_stats.totalSessionsWon / df_personal_champ_ranked_stats.totalSessionsPlayed
            df_personal_champ_ranked_stats = df_personal_champ_ranked_stats.T

            #get total win ratio
            total_win_ratio = sum(df_personal_champ_ranked_stats.T['totalSessionsWon'])/sum(df_personal_champ_ranked_stats.T['totalSessionsPlayed'])
            total_win_ratio = '{percent:.2%}'.format(percent=total_win_ratio)

            # get top ranked champs
            top_champs = df_personal_champ_ranked_stats.T.sort_values(by='totalSessionsPlayed', ascending=False)[0:8]

            champ_list = []
            # show relevant stats for champs
            for c in top_champs.T:
                name = champ_dict[c]
                games_played = top_champs.T[c].totalSessionsPlayed
                kda = '{:.3f}'.format(top_champs.T[c].KDA)
                win_ratio = '{percent:.1%}'.format(percent=top_champs.T[c].winRatio)
                mastery = getSummonerChampLevel(c, sumID)
                champ_url = 'http://ddragon.leagueoflegends.com/cdn/'+version+'/img/champion/'+name.replace(' ', '')+'.png'
                list_item = {'name': name, 'games_played': games_played, 'kda': kda, 'win_ratio': win_ratio,
                             'mastery': mastery, 'champ_url': champ_url}
                champ_list.append(list_item)

        time.sleep(10)
        # get highestAchievedSeasonTier
        highestAchievedSeasonTier = 'unranked'
        recent_games_url = 'https://na.api.riotgames.com/api/lol/NA/v1.3/game/by-summoner/' + sumID + '/recent?api_key=' + key
        recent_games = requests.get(recent_games_url).json()
        r_champ_id = recent_games['games'][0]['championId']
        r_match_id = recent_games['games'][0]['gameId']
        r_game_url = 'https://na1.api.riotgames.com/lol/match/v3/matches/' + str(r_match_id) + '?api_key=' + key
        r_game = requests.get(r_game_url).json()
        for p in r_game['participants']:
            if p['championId'] == r_champ_id:
                highestAchievedSeasonTier = p['highestAchievedSeasonTier']
        highestAchievedSeasonTier = highestAchievedSeasonTier.lower()

        # get role pref
        matchlist_url = 'https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/' + account_id + '?season=' + current_season + '&api_key=' + key
        matchlist_data = requests.get(matchlist_url)
        matchlist = matchlist_data.json()['matches']
        num_matches = len(matchlist)
        top = 0
        jungle = 0
        mid = 0
        bot = 0
        support = 0
        for match in matchlist:
            if match['lane'] == 'BOTTOM' or match['lane'] == 'BOT':
                if match['role'] == 'DUO_SUPPORT':
                    support += 1
                else:
                    bot += 1
            elif match['lane'] == 'MID' or match['lane'] == 'MIDDLE':
                mid += 1
            elif match['lane'] == 'JUNGLE':
                jungle += 1
            elif match['lane'] == 'TOP':
                top += 1
        role_count_list = {'Top': top, 'Jungle': jungle, 'Mid': mid, 'ADC': bot, 'Support': support}
        most = 0
        second = 0
        main_role = 'None'
        secondary_role = 'None'
        for role in role_count_list:
            if role_count_list[role] > most:
                secondary_role = main_role
                second = most
                main_role = role
                most = role_count_list[role]
            elif role_count_list[role] > second:
                secondary_role = role
                second = role_count_list[role]

        return render(request, 'summoner_lookup.html', {'summoner_name': sum_name, 'rank': textRank, 'icon_url': icon_url,
                                                        'champ_list': champ_list, 'main_role': main_role,
                                                        'secondary_role':secondary_role, 'total_win_ratio':total_win_ratio,
                                                        'highestAchievedSeasonTier':highestAchievedSeasonTier, 'form': form})

#new idea would be a guess that champion by their title aka "The Barbarian King" : Tryndamere