import csv
import os

from app.scrapping import get_classification_table, get_days, get_results_per_day
from app.utils import write_classification_table, get_league_name_from_id


def create_csv():
    # Get Selected leagues by the user
    leagues = os.getenv("LEAGUES_ID").split(",")

    # Scrap and creat the files
    for league_id in leagues:
        get_all_results(league_id)
        h, rows = get_classification_table(league_id)
        write_classification_table(league_id, h, rows)


def get_all_results(c_id):
    """
    Get the results of each day and creates the rows to be used in the CSV
    :param c_id: League ID
    :return:
    """
    # Prepare the directory and file
    league_name = get_league_name_from_id(c_id)
    data_directory = os.path.join("data", league_name)
    os.makedirs(data_directory, exist_ok=True)
    path_file = f"data/{league_name}/results_table.csv"
    # Headers
    headers = (
        "JORNADA, DIA, HORA, EQUIPOS, SET 1, SET 2, SET 3, SET 4, SET 5, TOTAL".split(
            ","
        )
    )
    days = get_days(c_id)
    with open(path_file, "w", newline="", encoding="utf-8") as o:
        w = csv.writer(o)
        # Headers
        w.writerow(headers)
        # Rows
        for day in days:
            w.writerow([day])
            day_results = get_results_per_day(c_id, day)
            day_results.sort(key=lambda x: (x.date, x.hour))
            for day_result in day_results:
                w.writerow(["", day_result.date, day_result.hour] + day_result.team_a)
                w.writerow(3 * [""] + day_result.team_b)
                w.writerow([])
