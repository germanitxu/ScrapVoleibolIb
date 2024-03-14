import os
import sys
import dotenv
import shutil
import re
from crontab import CronTab
import json

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


def save_leagues_ids(ids):
    """
    Save the ids in the .env file
    :param ids: ids of leagues, as a string
    :return: None
    """
    # Create .env file from the template if user hasn't done it yet
    if not os.path.exists(".env"):
        shutil.copy(".env.template", ".env")

    dotenv.set_key(dotenv_file, "LEAGUES_ID", ids)


def create_json_leagues(leagues_dict):
    """
    Creates a json files with a relation of league names and IDs
    :param leagues_dict: Ids of leagues
    :return:
    """
    os.makedirs("temp", exist_ok=True)
    path_file = "temp/leagues_names_id.json"
    json_data = {i: league for league, i in leagues_dict.items()}
    with open(path_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f)


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
    leagues = os.getenv("LEAGUES_ID").split(",")
    return leagues


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
    job = cron.new(command=f'{sys.executable} main.py update', comment="scrappingVIB")
    job.minute.every(2)
    cron.write()


def get_league_name_from_id(c_id) -> str:
    """
    Sanitizes and return the name of the league
    :param c_id: League ID
    :return: League Name
    """
    leagues_ids_names = read_json_leagues()
    name = leagues_ids_names[c_id]
    sanitized_name = re.sub("\\W+", ' ', name).strip().replace(" ", "_")
    return sanitized_name
