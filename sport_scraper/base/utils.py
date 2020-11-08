def get_subdir(league):
    if league in ["college-football", "mens-college-basketball"]:
        subdir = "id"
    else:
        subdir = "name"

    return subdir


def get_season(type):
    if type.split("/")[2] == "1":
        season = "Preseason"
    elif type.split("/")[2] == "2":
        season = "Regular Season"
    elif type.split("/")[2] == "3":
        season = "Postseason"

    return season
