import typer
from InquirerPy import prompt
from InquirerPy.base import Choice
from InquirerPy.separator import Separator
from rich import print as rp
import os
from scripts.scrapping import get_leagues, get_classification_table, get_all_results
from scripts.utils import save_leagues_ids, get_saved_leagues, create_json_leagues

app = typer.Typer()


@app.command("leagues", help="Select 1 to many leagues you want to follow")
def select_leagues():
    """
    * Select the leagues you want the app to subscribe and download the results.
    """
    leagues_per_regions = get_leagues()
    league_key_value = {}
    leagues_choices = []
    saved_leagues = get_saved_leagues()
    for region, leagues in leagues_per_regions.items():
        leagues_choices.append(Separator(region))
        for league_name, values in leagues.items():
            enabled = values["id"] in saved_leagues
            leagues_choices.append(Choice(league_name, enabled=enabled))
            league_key_value[league_name] = values["id"]
    create_json_leagues(league_key_value)
    questions = [
        {
            "type": "checkbox",
            "qmark": ">>",
            "message": "Select on or multiples leagues to follow",
            "name": "leagues",
            "choices": leagues_choices,
            "validate": lambda answer: "You must choose at least one league." if len(answer) == 0 else True
        },
        # Cron work will be disabled until further testing
        # TODO test on unix machines
        # {
        #     "type": "confirm",
        #     "message": "Do you want to create an automatic task to scrap every monday?",
        #     "name": "create_cron",
        #     "default": False,
        # }

    ]
    answers = prompt(questions)
    # if answers["create_cron"]:
    #     system = platform.system()
    #     if system != "Windows":
    #         create_cron()
    #         rp("[green bold] Task created![green bold]")
    #     else:
    #         # TODO Create schtask for windows. What I saw looked really sad
    #         rp("[red bold]:warning: Scheduling task for Windows is disabled for now. :warning: [red bold]")
    # else:
    #     delete_cron()
    #     rp("[yellow bold] You can always manually download updated data using the command 'update'.[yellow bold]")
    ids = ",".join([league_key_value[answer] for answer in answers["leagues"]])
    save_leagues_ids(ids)
    rp("[green bold]Leagues saved successfully![green bold]")


@app.command("update", help="Activate the scrap and download the files.")
def update():
    """
    Creates the csv from the selected leagues
    :return:
    """
    create_csv()
    rp("[green bold]Files generated! Check the data folder.[green bold]")


def create_csv():
    # Get Selected leagues by the user
    leagues = os.getenv("LEAGUES_ID").split(",")

    # Scrap and creat the files
    for league_id in leagues:
        get_all_results(league_id)
        get_classification_table(league_id)


if __name__ == "__main__":
    app()
