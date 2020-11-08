base_url = "http://www.espn.com"
sitemap_url = base_url + "/espn/sitemap"
teams_url = base_url + "/{league}/teams"
schedule_url = (
    base_url + "/{league}/team/schedule/_/{subdir}/{team}/season/{year}{type}"
)
roster_url = base_url + "/{league}/team/roster/_/{subdir}/{team}"
game_url = base_url + "/{league}/matchup?gameId={game_id}"

season_types = {
    "nfl": [""],
    "mlb": [
        "/seasontype/1",
        "/seasontype/2/half/1",
        "/seasontype/2/half/2",
        "/seasontype/3",
    ],
    "nba": ["/seasontype/1", "/seasontype/2", "/seasontype/3"],
    "nhl": ["/seasontype/1", "/seasontype/2", "/seasontype/3"],
    "college-football": [""],
    "mens-college-basketball": [""],
}
