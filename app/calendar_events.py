import os.path
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.scrapping import get_days, get_results_per_day
from app.utils import get_my_leagues_name_id, get_saved_teams

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def google_login():
    """
    Log in Google to use calendar app
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("google_creds/token.json"):
        creds = Credentials.from_authorized_user_file("google_creds/token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "google_creds/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("google_creds/token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("calendar", "v3", credentials=creds)
    except HttpError as error:
        print(f"An error occurred: {error}")


def get_google_service():
    google_login()  # Creates Token file
    creds = Credentials.from_authorized_user_file("google_creds/token.json", SCOPES)
    return build("calendar", "v3", credentials=creds)


def create_calendar(summary, service):
    calendar_list_entry = {"summary": summary, "timeZone": "Europe/Madrid"}
    created_calendar_list_entry = (
        service.calendars().insert(body=calendar_list_entry).execute()
    )
    return created_calendar_list_entry["id"]


def create_calendar_league_events():
    # For each League, create a CALENDAR
    # For each Match, create an EVENT in said CALENDAR
    service = get_google_service()
    leagues = get_my_leagues_name_id()
    calendar_list = service.calendarList().list().execute()
    calendar_names_ids = {cal["summary"]: cal["id"] for cal in calendar_list["items"]}
    for league_id, league_name in leagues.items():
        # if league not in calendar already, add it
        cal_id = (
            calendar_names_ids[league_name]
            if league_name in calendar_names_ids
            else create_calendar(league_name, service)
        )
        days = get_days(league_id)
        for day in days:
            try:
                event = {"summary": f"Partidos {league_name} jornada #{day}:"}
                day_matches = get_results_per_day(league_id, day)
                day_matches.sort(key=lambda x: (x.date, x.hour))
                description = "<ul>"
                start_datetime = end_datetime = datetime.strptime(
                    day_matches[0].date, "%d/%m/%Y"
                )
                for match in day_matches:
                    description += f"<li>{match.date}: <b>{match.team_a[0]}</b> vs <b>{match.team_b[0]}</b>"
                    match_start_datetime = match_end_datetime = datetime.strptime(
                        match.date, "%d/%m/%Y"
                    )
                    start_datetime = (
                        match_start_datetime
                        if match_start_datetime < start_datetime
                        else start_datetime
                    )
                    end_datetime = (
                        match_end_datetime
                        if match_end_datetime > end_datetime
                        else end_datetime
                    )
                    if len(match.hour) == 5:
                        description += f": ({match.hour})"

                    description += ". </li>"

                start = {
                    "date": start_datetime.strftime("%Y-%m-%d"),
                    "timeZone": "Europe/Madrid",
                }
                # end is exclusive, so we add 1 day to include the end day
                end_datetime = end_datetime + timedelta(days=1)
                end = {
                    "date": end_datetime.strftime("%Y-%m-%d"),
                    "timeZone": "Europe/Madrid",
                }
                description += "</ul>"
                event["description"] = description
                event["start"] = start
                event["end"] = end
                service.events().insert(calendarId=cal_id, body=event).execute()
            except HttpError as error:
                print(f"An error occurred: {error}")


def create_calendar_team_events():
    service = get_google_service()
    leagues_teams = get_saved_teams()
    calendar_list = service.calendarList().list().execute()
    calendar_names_ids = {cal["summary"]: cal["id"] for cal in calendar_list["items"]}
    leagues = get_my_leagues_name_id()
    for league_name, teams in leagues_teams.items():
        league_id = list(leagues.keys())[list(leagues.values()).index(league_name)]
        for team in teams:
            try:
                cal_name = f"{team} ({league_name})"
                # if league not in calendar already, add it
                cal_id = (
                    calendar_names_ids[team]
                    if team in calendar_names_ids
                    else create_calendar(cal_name, service)
                )
                days = get_days(league_id)
                for day in days:
                    event = {"summary": f"Partido {team} jornada #{day}:"}
                    day_matches = get_results_per_day(league_id, day)
                    team_match = [
                        match
                        for match in day_matches
                        if match.team_a[0] == team or match.team_b[0] == team
                    ]
                    if not team_match:
                        # Team doesn't play that day
                        continue
                    team_match = team_match[0]
                    description = f"<li>{team_match.date}: <b>{team_match.team_a[0]}</b> vs <b>{team_match.team_b[0]}</b>"
                    start_datetime = datetime.strptime(team_match.date, "%d/%m/%Y")
                    if len(team_match.hour) == 5:
                        description += f": ({team_match.hour})"
                    start = {
                        "date": start_datetime.strftime("%Y-%m-%d"),
                        "timeZone": "Europe/Madrid",
                    }
                    end = {
                        "date": start_datetime.strftime("%Y-%m-%d"),
                        "timeZone": "Europe/Madrid",
                    }
                    event["description"] = description
                    event["start"] = start
                    event["end"] = end
                    service.events().insert(calendarId=cal_id, body=event).execute()
            except Exception as e:
                print(e)
            except HttpError as error:
                print(f"An error occurred: {error}")
