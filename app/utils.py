import csv
import json
import os
import re
import shutil
import sys

import dotenv
from crontab import CronTab

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


def save_leagues_ids(ids):
    """
    Save the ids in the .env file
    :param ids: ids of Leagues, as a string
    :return: None
    """
    # Create .env file from the template if user hasn't done it yet
    if not os.path.exists(".env"):
        shutil.copy(".env.template", ".env")

    dotenv.set_key(dotenv_file, "LEAGUES_ID", ids)


def save_teams(json_data):
    """
    Save the names in the .env file
    :param teams_names: Names of the teams, as a string
    :return: None
    """
    path_file = "temp/saved_leagues_teams.json"
    with open(path_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f)
    # Create .env file from the template if user hasn't done it yet
    # if not os.path.exists(".env"):
    #     shutil.copy(".env.template", ".env")
    #
    # dotenv.set_key(dotenv_file, "TEAMS", teams_names)


def create_json_leagues(leagues_dict):
    """
    Creates a json files with a relation of league names and ID's
    :param leagues_dict: ID's of Leagues
    :return:
    """
    os.makedirs("temp", exist_ok=True)
    path_file = "temp/leagues_names_id.json"
    json_data = {i: league.strip() for league, i in leagues_dict.items()}
    with open(path_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f)


def write_classification_table(c_id, headers, rows):
    # Preparing the directory and file to dump the data
    league_name = get_league_name_from_id(c_id)
    data_directory = os.path.join("../data", league_name)
    os.makedirs(data_directory, exist_ok=True)
    path_file = f"data/{league_name}/classification_table.csv"
    with open(path_file, "w") as o:
        w = csv.writer(o)
        # Headers
        w.writerow(headers)
        # Rows
        for r in rows:
            w.writerow(r)


def update_json_teams(league_id, rows):
    """
    Creates a json files with a relation of league names, ids and their teams
    :param league_id: ID of the leagues to update
    :param rows: rows from the classification table
    :return:
    """
    teams_league = get_json_teams()
    league_name = read_json_leagues()[league_id]
    teams = []
    for row in rows:
        teams.append(row[1])
    teams_league[league_name] = teams
    path_file = "temp/leagues_teams.json"
    with open(path_file, "w", encoding="utf-8") as f:
        json.dump(teams_league, f)


def get_json_teams():
    """
    Reads the json leagues teams
    """
    path_file = "temp/leagues_teams.json"
    data = {}
    if not os.path.exists(path_file):
        open(path_file, "w").close()
    f = open(path_file)
    if os.stat(path_file).st_size != 0:  # file not empty
        data = json.load(f)
    f.close()
    return data


def read_json_leagues():
    """
    Reads the json leagues id: name file
    :return:
    """
    f = open("temp/leagues_names_id.json")
    data = json.load(f)
    return data


def get_saved_leagues() -> [str]:
    """
    Returns the ids saved if they exist
    :return: List of ids
    """
    leagues = os.getenv("LEAGUES_ID", "").split(",")
    return leagues


def get_saved_teams() -> [str]:
    """
    Returns the names of teams saved if they exist
    :return: List of names
    """
    # teams = os.getenv("TEAMS", "").split(",")
    # return teams
    path_file = "temp/saved_leagues_teams.json"
    data = {}
    if not os.path.exists(path_file):
        open(path_file, "w").close()
    f = open(path_file)
    if os.stat(path_file).st_size != 0:  # file not empty
        data = json.load(f)
    f.close()
    return data


def delete_cron():
    """
    Deletes existing cron
    :return:
    """
    cron = CronTab(user=True)
    cron.remove_all(comment="scrappingVIB")


def create_cron():
    """
    Creates cron job
    :return:
    """
    cron = CronTab(user=True)
    job = cron.new(command=f"{sys.executable} main.py update", comment="scrappingVIB")
    job.minute.every(2)
    cron.write()


def get_league_name_from_id(c_id) -> str:
    """
    Sanitizes and return the name of the League

    :param c_id: League's ID
    :return: League Name
    """
    leagues_ids_names = read_json_leagues()
    name = leagues_ids_names[c_id]
    sanitized_name = re.sub("\\W+", " ", name).strip().replace(" ", "_")
    return sanitized_name


def get_my_leagues_name_id():
    my_leagues_ids = get_saved_leagues()
    all_leagues = read_json_leagues()
    my_leagues = {}
    for id, name in all_leagues.items():
        if id in my_leagues_ids:
            my_leagues[id] = name
    return my_leagues
