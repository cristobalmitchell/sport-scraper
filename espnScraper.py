#!/usr/bin/python

# PROGRAM:		ESPN.com Web Scraper
# DESCRIPTION:	This program creates a scraper class object
#				with various functions for pulling leagues,
#				teams, schedules, and game data for the major
#				league sports available on ESPN.com
# AUTHOR:		Cristobal Mitchell
# CREATED:		08/10/2017
# MODIFIED:		05/21/2020
# VERSION:		2.0

# DEBUG FLAG
debug = False

import pandas as pd
import numpy as np
import re
import requests
from bs4 import BeautifulSoup


class espnScraper:
	def __init__(self):
		self.base_url = 'http://www.espn.com'
		self.sitemap = self.base_url + '/espn/sitemap'
		self.years = [2016,2017,2018]
		self.season_types = { 'nfl' : [''],
							'mlb' : ['/seasontype/1','/seasontype/2/half/1','/seasontype/2/half/2','/seasontype/3'],
							'nba' : ['/seasontype/1','/seasontype/2','/seasontype/3'],
							'nhl' : [''], 
							'college-football' : [''],
							'mens-college-basketball' : ['']
							}


	def leagues(self):
		# returns a list of leagues available on the site
		leagues = []
		r = requests.get(self.sitemap)
		soup = BeautifulSoup(r.text, 'html.parser')
		ul = soup.find_all('ul')		

		for u in ul[0].find_all('ul'):
		    try:
		        league = u.find_all('li')[2].a['href'].split('espn.com/')[-1].split('/')[0]
		        leagues.append(league)
		    except:
		        pass
				
		return leagues

	def teams(self,league):
		# returns a dataframe of teams from targeted league
		url = 'http://www.espn.com/{0}/teams'.format(league)
		league_list = []
		division_list = []
		team_list = []
		prefix_1_list = []
		prefix_2_list = []
		team_url_list = []

		
		r = requests.get(url.format(league))
		soup = BeautifulSoup(r.text, 'html.parser')
		divs = soup.find_all('div', class_ = 'mt7')

	    for div in divs:
	        division = div.div.string
	        
	        for subdiv in div.find_all('div', class_ = 'mt3'):
	            team = subdiv.a.img['alt']
	            prefix1 = subdiv.a['href'].split('/')[-2] # team URL parent directory
	            prefix2 = subdiv.a['href'].split('/')[-1] # team URL child directory
	            team_url = base_url + subdiv.a['href']

	            league_list.append(league)
	            division_list.append(division)
	            team_list.append(team)
	            prefix_1_list.append(prefix1)
	            prefix_2_list.append(prefix2)
	            team_url_list.append(team_url)
		
		dic = {
			'team': team_list, 
			'url': team_url_list, 
			'prefix_2': prefix_2_list, 
			'prefix_1': prefix_1_list, 
			'league': league_list, 
			'division': division_list
			}

		df = pd.DataFrame(dic)
		
		return df

	def schedule(self, league, team, year):
		# returns a dataframe of the schedule
		df = pd.DataFrame()
		for t in self.season_types[league]:
			try:
				url = 'http://www.espn.com/{0}/team/schedule/_/name/{1}/season/{2}{3}'.format(league,team,year,t)
				
				dic = {}
				dic.setdefault('season', [])
				dic.setdefault('year', [])

				r = requests.get(url)
				soup = BeautifulSoup(r.text, 'html.parser')
				table = soup.find_all('tbody', class_ = 'Table__TBODY')[0]

				for row in table.find_all('tr'):
				    if row.string is not None:
				        season = row.string
				    elif row.find_all('td', class_='Table_Headers'):
				    	headers = []
				        for value in row.find_all('td'):
				            if value.string not in headers:
				                headers.append(value.string)
				    elif row.find_all('td')[1].text != 'BYE WEEK':
				        dic['season'].append(season)
				        dic['year'].append(year)
				        for i in range(len(headers)):
			                column = headers[i]
			                if column.lower() == 'opponent':
			                    home = not row.find_all('td')[i].text.split()[0] == '@'
			                    if home:
			                        home_team = team
			                        try:
			                            away_team = row.find_all('td')[i].a['href'].split('/')[-2]
			                        except:
			                            away_team = row.find_all('td')[i].text
			                    else:
			                        away_team = team
			                        try:
			                            home_team = row.find_all('td')[i].a['href'].split('/')[-2]
			                        except:
			                            home_team = row.find_all('td')[i].text   
			                        
			                    try:
			                        dic['home_team'].append(home_team)
			                        dic['away_team'].append(away_team)
			                    except:
			                        dic.setdefault('home_team', [])
			                        dic.setdefault('away_team', [])
			                        dic['home_team'].append(home_team)
			                        dic['away_team'].append(away_team)

			                elif column.lower() == 'result':
			                    if row.find_all('td')[i].text != 'Postponed':
			                        game_id = row.find_all('td')[i].a['href'].split('/')[-1]

			                        if home:
			                            if row.find_all('td')[3].span.text in ['W','T','D']:
			                                home_team_score = row.find_all('td')[3].a.text.strip().split('-')[0]
			                                away_team_score = row.find_all('td')[3].a.text.strip().split('-')[1]
			                            elif row.find_all('td')[3].span.text == 'L':
			                                home_team_score = row.find_all('td')[3].a.text.strip().split('-')[1]
			                                away_team_score = row.find_all('td')[3].a.text.strip().split('-')[0]

			                        if not home:
			                            if row.find_all('td')[3].span.text in ['W','T','D']:
			                                away_team_score = row.find_all('td')[3].a.text.strip().split('-')[0]
			                                home_team_score = row.find_all('td')[3].a.text.strip().split('-')[1]
			                            elif row.find_all('td')[3].span.text == 'L':
			                                away_team_score = row.find_all('td')[3].a.text.strip().split('-')[1]
			                                home_team_score = row.find_all('td')[3].a.text.strip().split('-')[0]
			                                
			                    else:
			                        game_id = ''
			                        home_team_score = ''
			                        away_team_score = ''
			                    
			                    try:
			                        dic['game_id'].append(game_id)
			                        dic['home_team_score'].append(home_team_score)
			                        dic['away_team_score'].append(away_team_score)
			                    except:
			                        dic.setdefault('game_id', [])
			                        dic.setdefault('home_team_score', [])
			                        dic.setdefault('away_team_score', [])
			                        dic['game_id'].append(game_id)
			                        dic['home_team_score'].append(home_team_score)
			                        dic['away_team_score'].append(away_team_score)
			                        

			                
			                else:
			                    try:
			                        dic[column].append(row.find_all('td')[i].text)
			                    except:
			                        dic.setdefault(column, [])
			                        try:
			                            dic[column].append(row.find_all('td')[i].text)
			                        except:
			                            dic[column].append('')
				df = pd.concat([df,pd.DataFrame(dic)], ignore_index = True)
			except:
				pass

		return df

	def game_information(self, league, gameId):
        game = {'datetime':[], 
              'network': [], 
              'attendance': [], 
              'capacity': [], 
              'location': [], 
              'venue': []}
        
        url = "{0}/{1}/matchup?gameId={2}".format(self.base_url, league, gameId)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        article = soup.find_all('article', class_ ='sub-module game-information')
        
        try:
            game['datetime'].append(article[0].find_all('span')[0]['data-date'])
            
            try:
                game['network'].append(article[0].find_all('div', class_='game-network')[0].text)
            except:
                pass
            
            for i in range(len(article[0].find_all('div', class_='game-info-note capacity'))):
               key = article[0].find_all('div', class_='game-info-note capacity')[i].text.split(': ')[0].lower()
               value = article[0].find_all('div', class_='game-info-note capacity')[i].text.split(': ')[1].lower()
               game[key].append(value)
            
            game['location'].append(article[0].find_all('li', class_='icon-font-before icon-location-solid-before')[0].text)
            
            try:
                 game['venue'].append(article[0].find_all('div', class_='game-field')[0].div.div.text)
            except:
                game['venue'].append(article[0].find_all('div', class_='game-field')[0].div.text)

            for k in game.keys():
                for v in range(len(game[k])):
                    game[k][v] = re.sub('\t|\n','',game[k][v])

            return game 

        except:
            pass

