import os
import sys
import dotenv
import shutil
from .scrapping import get_classification_table, get_all_results

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)


def create_csv():
    # Get Selected leagues by the user
    leagues = os.getenv("LEAGUES_ID").split(",")

    # Scrap and creat the files
    for league_id in leagues:
        get_all_results(league_id)
        get_classification_table(league_id)


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


def get_saved_leagues() -> [str]:
    """
    Returns the ids saved if they exist
    :return: List of ids
    """
    leagues = os.getenv("LEAGUES_ID").split(",")
    return leagues


def create_cron():
    from crontab import CronTab
    cron = CronTab(user=True)
    job = cron.new(command=f'{sys.executable} scripts/create_csv.py')
    job.minute.every(2)
    cron.write()
