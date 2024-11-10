import typer
from InquirerPy import prompt
from InquirerPy.base import Choice
from InquirerPy.separator import Separator
from rich import print as rp

from app.calendar_events import (
    create_calendar_league_events,
    create_calendar_team_events,
)
from app.scrapping import get_leagues, get_classification_table
from app.utils import (
    save_leagues_ids,
    get_saved_leagues,
    create_json_leagues,
    update_json_teams,
    get_json_teams,
    get_saved_teams,
    save_teams,
)
from app.data_csv import create_csv

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
            "message": "Select one or multiples leagues to follow",
            "name": "leagues",
            "choices": leagues_choices,
            "validate": lambda answer: (
                "You must choose at least one league." if len(answer) == 0 else True
            ),
        },
    ]
    answers = prompt(questions)

    leagues_ids = [league_key_value[answer] for answer in answers["leagues"]]
    ids = ",".join(leagues_ids)
    save_leagues_ids(ids)
    for league_id in leagues_ids:
        h, rows = get_classification_table(league_id)
        update_json_teams(league_id, rows)
    rp("[green bold]Leagues saved successfully![green bold]")


@app.command("update", help="Activate the scrap and download the files.")
def update():
    """
    Creates the csv from the selected leagues
    :return:
    """
    create_csv()
    rp("[green bold]Files generated! Check the data folder.[green bold]")


@app.command(
    "calendar_add_leagues", help="Add the followed leagues matches to calendar."
)
def calendar_add_leagues():
    """
    Adds to calendar an event for each match
    :return:
    """
    create_calendar_league_events()
    rp("[green bold]Events generated! Check the calendar.[green bold]")


@app.command(
    "calendar_add_team",
    help="Select 1 to many teams from your leagues to follow on your calendar.",
)
def calendar_add_teams():
    """
    Adds to calendar an event for each match of the teams selected
    :return:
    """
    league_teams = get_json_teams()

    saved_teams = get_saved_teams()
    user_choice_teams = {}
    for league_name, teams in league_teams.items():
        teams_choices = []
        league_name_stripped = league_name.replace(" ", "_")
        teams_choices.append(Separator(league_name))
        for team in teams:
            enabled = team in saved_teams[league_name]
            teams_choices.append(Choice(team, enabled=enabled))
        question = {
            "type": "checkbox",
            "qmark": ">>",
            "message": f"Select one or multiples teams to follow for {league_name}",
            "name": f"teams_{league_name_stripped}",
            "choices": teams_choices,
            "validate": lambda answer: (
                "You must choose at least one team." if len(answer) == 0 else True
            ),
        }
        answers = prompt(question)
        user_choice_teams[league_name] = answers[f"teams_{league_name_stripped}"]
    save_teams(user_choice_teams)
    rp("[yellow bold]Creating events....[yellow bold]")
    create_calendar_team_events()
    rp("[green bold]Events generated! Check the calendar.[green bold]")


if __name__ == "__main__":
    app()
