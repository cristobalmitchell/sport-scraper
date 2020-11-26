"""
Base class for sport_scraper
"""

import datetime as dt
import re

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from .config import *
from .utils import *


class SportScraper:
    def __init__(self):
        self.base_url = base_url
        self.sitemap_url = sitemap_url
        self.teams_url = teams_url
        self.schedule_url = schedule_url
        self.roster_url = roster_url
        self.game_url = game_url
        self.season_types = season_types

    def leagues(self):
        # returns a list of leagues available on the site
        leagues = []
        r = requests.get(self.sitemap_url)
        soup = BeautifulSoup(r.text, "html.parser")
        ul = soup.find_all("ul")

        for u in ul[0].find_all("ul"):
            try:
                league = (
                    u.find_all("li")[2].a["href"].split("espn.com/")[-1].split("/")[0]
                )
                leagues.append(league)
            except:
                pass

        return leagues

    def teams(self, league):
        # returns a dataframe of teams from targeted league
        league_list = []
        division_list = []
        team_list = []
        prefix_1_list = []
        prefix_2_list = []
        team_url_list = []

        url = self.teams_url.format(league=league)
        r = requests.get(url.format(league))
        soup = BeautifulSoup(r.text, "html.parser")
        divs = soup.find_all("div", class_="mt7")

        for div in divs:
            division = div.div.string

            for subdiv in div.find_all("div", class_="mt3"):
                team = subdiv.a.img["alt"]
                prefix1 = subdiv.a["href"].split("/")[-2]  # team URL parent directory
                prefix2 = subdiv.a["href"].split("/")[-1]  # team URL child directory
                team_url = self.base_url + subdiv.a["href"]

                league_list.append(league)
                division_list.append(division)
                team_list.append(team)
                prefix_1_list.append(prefix1)
                prefix_2_list.append(prefix2)
                team_url_list.append(team_url)

        dic = {
            "team": team_list,
            "url": team_url_list,
            "prefix_2": prefix_2_list,
            "prefix_1": prefix_1_list,
            "league": league_list,
            "division": division_list,
        }

        df = pd.DataFrame(dic)

        return df

    def schedule(self, league, team, year):
        # returns a dataframe of the schedule
        df = pd.DataFrame()
        for t in self.season_types[league]:
            try:
                subdir = get_subdir(league)
                url = self.schedule_url.format(
                    league=league, subdir=subdir, team=team, year=year, type=t
                )
                r = requests.get(url)
                soup = BeautifulSoup(r.text, "html.parser")
                table = soup.find_all("tbody", class_="Table__TBODY")[0]

                if t != "":
                    season = get_season(t)

                for row in table.find_all("tr"):
                    if row.string is not None:
                        season = row.string
                    elif row.find_all("td", class_="Table_Headers"):
                        headers = []
                        for value in row.find_all("td"):
                            if value.string not in headers:
                                headers.append(value.string)
                    elif row.find_all("td")[1].text != "BYE WEEK":
                        record = {
                            "game_id": "",
                            "season": "",
                            "year": "",
                            "date": "",
                            "home_team": "",
                            "away_team": "",
                            "home_team_score": "",
                            "away_team_score": "",
                            "note": "",
                        }
                        try:
                            record["season"] = season
                        except:
                            pass
                        record["year"] = year
                        for i in range(len(headers)):
                            column = headers[i]
                            if column.lower() == "opponent":
                                home = not row.find_all("td")[i].text.split()[0] == "@"
                                if home:
                                    home_team = team
                                    try:
                                        away_team = (
                                            row.find_all("td")[i]
                                            .a["href"]
                                            .split("/")[-2]
                                        )
                                    except:
                                        away_team = row.find_all("td")[i].text
                                else:
                                    away_team = team
                                    try:
                                        home_team = (
                                            row.find_all("td")[i]
                                            .a["href"]
                                            .split("/")[-2]
                                        )
                                    except:
                                        home_team = row.find_all("td")[i].text

                                record["home_team"] = home_team
                                record["away_team"] = away_team

                            elif column.lower() == "result":
                                if row.find_all("td")[i].text != "Postponed":
                                    game_id = (
                                        row.find_all("td")[i]
                                        .a["href"]
                                        .split("/")[-1][-9:]
                                    )

                                    if home:
                                        if row.find_all("td")[i].span.text in [
                                            "W",
                                            "T",
                                            "D",
                                        ]:
                                            home_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[0]
                                            )
                                            away_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[1]
                                            )
                                        elif row.find_all("td")[i].span.text == "L":
                                            home_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[1]
                                            )
                                            away_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[0]
                                            )

                                    if not home:
                                        if row.find_all("td")[i].span.text in [
                                            "W",
                                            "T",
                                            "D",
                                        ]:
                                            away_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[0]
                                            )
                                            home_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[1]
                                            )
                                        elif row.find_all("td")[i].span.text == "L":
                                            away_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[1]
                                            )
                                            home_team_score = (
                                                row.find_all("td")[i]
                                                .a.text.strip()
                                                .split("-")[0]
                                            )

                                    record["game_id"] = game_id
                                    record["home_team_score"] = home_team_score
                                    record["away_team_score"] = away_team_score
                                else:
                                    record["note"] = "postponed"

                            elif column.lower() == "date":
                                record["date"] = row.find_all("td")[i].text

                        df = df.append(pd.Series(record), ignore_index=True)
            except:
                pass

        return df

    def roster(self, league, team):
        df = pd.DataFrame()
        subdir = get_subdir(league)
        url = self.roster_url.format(league=league, subdir=subdir, team=team)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find_all("div", class_="ResponsiveTable Team Roster")[0]
        headers = []
        for value in table.find_all("th", class_="Table__TH"):
            if value.string not in headers:
                headers.append(value.string)
        for row in table.find_all("tr", class_="Table__TR"):
            if row.find_all("td", class_="Table__TD"):
                record = {
                    "name": "",
                    "position": "",
                    "height": "",
                    "weight": "",
                    "experience": "",
                    "player_id": "",
                    "player_name": "",
                }
                for i in range(len(headers)):
                    if headers[i]:
                        column = headers[i]
                        if column.lower() == "name":
                            record["name"] = (
                                row.find_all("td", class_="Table__TD")[i]
                                .find("a")
                                .string
                            )
                            record["player_id"] = (
                                row.find_all("td", class_="Table__TD")[i]
                                .find("a")["href"].split("id/")[-1].split("/")[0]
                            )
                            record["player_name"] = (
                                row.find_all("td", class_="Table__TD")[i]
                                .find("a")["href"].split("id/")[-1].split("/")[-1]
                            )
                        elif column.lower() == "pos":
                            record["position"] = row.find_all("td", class_="Table__TD")[
                                i
                            ].string
                        elif column.lower() == "ht":
                            record["height"] = row.find_all("td", class_="Table__TD")[
                                i
                            ].string
                        elif column.lower() == "wt":
                            record["weight"] = row.find_all("td", class_="Table__TD")[
                                i
                            ].string
                        elif column.lower() == "exp":
                            record["experience"] = row.find_all("td", class_="Table__TD")[
                                i
                            ].string

                df = df.append(pd.Series(record), ignore_index=True)

        return df

    def game_information(self, league, game_id):
        game = {
            "game_id": game_id,
            "datetime": "",
            "network": "",
            "attendance": "",
            "capacity": "",
            "location": "",
            "venue": "",
        }

        url = self.game_url.format(league=league, game_id=game_id)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        article = soup.find_all("article", class_="sub-module game-information")

        if not article:
            article = soup.find_all("section", class_="Card GameInfo")

        try:
            game["datetime"] = article[0].find_all("span")[0]["data-date"]
        except:
            try:
                game["datetime"] = article[0].find_all("span")[0].text
            except:
                pass

        try:
            game["network"] = article[0].find_all("div", class_="game-network")[0].text
        except:
            pass

        for i in range(
            len(article[0].find_all("div", class_="game-info-note capacity"))
        ):
            key = (
                article[0]
                .find_all("div", class_="game-info-note capacity")[i]
                .text.split(": ")[0]
                .lower()
            )
            value = (
                article[0]
                .find_all("div", class_="game-info-note capacity")[i]
                .text.split(": ")[1]
                .lower()
            )
            game[key] = value

        try:
            for i in ["Numbers", "Capacity"]:
                key = (
                    article[0]
                    .find_all("div", class_="Attendance")[0]
                    .find_all("div", class_="Attendance__{0}".format(i))[0]
                    .text.split(": ")[0]
                    .lower()
                )
                value = (
                    article[0]
                    .find_all("div", class_="Attendance")[0]
                    .find_all("div", class_="Attendance__{0}".format(i))[0]
                    .text.split(": ")[1]
                    .lower()
                )
                game[key] = value
        except:
            pass

        try:
            game["location"] = (
                article[0]
                .find_all("li", class_="icon-font-before icon-location-solid-before")[0]
                .text
            )
        except:
            try:
                game["location"] = (
                    article[0].find_all("section")[0].find_all("span")[1].text
                )
            except:
                pass

        try:
            game["venue"] = (
                article[0].find_all("div", class_="game-field")[0].div.div.text
            )
        except:
            try:
                game["venue"] = (
                    article[0].find_all("div", class_="game-field")[0].div.text
                )
            except:
                try:
                    game["venue"] = (
                        article[0].find_all("div")[1].div.figure.img["title"]
                    )
                except:
                    pass

        for k in game.keys():
            game[k] = re.sub("\t|\n", "", game[k])

        return game
