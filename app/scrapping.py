import requests
from bs4 import BeautifulSoup as Bs
import re
from urllib.parse import urlparse, parse_qs
import csv
import os
from .common import Result
from .utils import get_league_name_from_id


def format_sub_leagues_names(pre_name, name) -> str:
    pre_name = pre_name.strip()
    name = name.strip()
    return pre_name + ": " + name


def set_full_url(url):
    return "https://www.voleibolib.net/" + url


def get_leagues() -> dict:
    """

    :return: Dictionary of all leagues listed in the web, with the link and league ID
    """
    # The web dynamically fetches the competitions from the URL below
    url = "https://www.voleibolib.net/JSON/get_Menu_Competiciones.dcl"
    page = requests.get(url)
    soup = Bs(page.text, "html.parser")
    regions = soup.find_all(
        class_="panel-default", recursive=False
    )  # This fetches the regions of the leagues
    leagues_formatted = {}  # This object is what we will return
    for region in regions:
        region_name = region.find("h4", class_="panel-title").a.string.strip()
        leagues_formatted[region_name] = {}
        leagues = region.find_all("div", class_="panel-body")
        for league in leagues:
            sub_leagues = league.find_all("a", href=re.compile("clasificaciones"))

            for sub_league in sub_leagues:
                name = sub_league.text
                link = set_full_url(sub_league.get("href"))
                parsed_link = urlparse(link)
                if "Liga Regular" in name:
                    # In this case, the league name is its parent
                    name = (
                        sub_league.find_parent(class_="panel-body")
                        .find("a", recursive=False)
                        .text
                    )
                else:
                    # The name is in the <a>, but only the group, the league name is its parent too
                    pre_name = (
                        sub_league.find_parent(class_="panel-body")
                        .find("a", recursive=False)
                        .text
                    )
                    name = format_sub_leagues_names(pre_name, name)
                league_id = parse_qs(parsed_link.query)["id"][0]
                leagues_formatted[region_name][name] = {"id": league_id, "url": link}

    return leagues_formatted


def get_classification_table(c_id, day=""):
    """
    Gets the classification table update to the latest day
    :param c_id: ID of the league
    :param day: To fetch results of the league up to that day
    :return:
    """
    url = f"https://www.voleibolib.net/JSON/get_clasificacion.asp?id={c_id}&jor={day}"
    page = requests.get(url)
    soup = Bs(page.text, "html.parser")
    # Get the HTML table
    classification_table = soup.find(class_="clasificacion")
    headers = [th.text for th in classification_table.select("tr th")]
    headers[0] = (
        "#"  # First header is just an empty value, belonging to the team position
    )
    rows = [
        [td.text for td in row.find_all("td")]
        for row in classification_table.select("tr + tr")
    ]

    return headers, rows


def get_results_per_day(c_id, day="") -> [Result]:
    """
    Returns a list of Result for that day of competition
    :param c_id: ID of the league
    :param day: To fetch results of the league of that day
    :return: list[Result]
    """
    url = f"https://www.voleibolib.net/JSON/get_resultados.asp?id={c_id}&jor={day}"
    page = requests.get(url)
    soup = Bs(page.text, "html.parser")
    result_day = soup.find("h3", recursive=False).text.split()[1]
    info_matches = soup.find_all(class_="info_partido")
    results: list[Result] = []
    for info in info_matches:
        top = info.find(class_="top")  # This div has the Date, location and hour
        fecha_items = top.find(class_="fecha").text.split("-")
        date = fecha_items[0]
        hour = (
            fecha_items[-1] if len(fecha_items) else ""
        )  # Sometimes we find only the date
        # location = top.find(class_="municipio").text # Location was missing half the times. I can't make any use of it anyway so I am going to skip it # noqa
        info_match = info.find(
            class_="datos_partido"
        )  # This div has the names and results of each set
        result = info_match.find(class_="marcador").text.split("-")
        team_a_name, team_b_name = [
            team.text for team in info_match.find_all(class_="nombreEquipo")
        ]
        if team_b_name == "Descansa":
            # There is no team b
            continue
        # If the match was not played, both scorers are empty, and the rest of the data is going to be empty also
        sets_info = info.find(class_="estado_partido").find(class_="marcador").text
        total_sets = len(sets_info.split("/")) if len(sets_info.split("/")) > 1 else 0
        if total_sets:
            # The offset between the last set and the total result.
            offset = (5 - total_sets) * [""]
            results_compacted = [
                game_set.split("-") for game_set in sets_info.split("/")
            ]
            team_a_row = (
                [team_a_name]
                + [sets[0] for sets in results_compacted]
                + offset
                + [result[0]]
            )
            team_b_row = (
                [team_b_name]
                + [sets[1] for sets in results_compacted]
                + offset
                + [result[1]]
            )
        else:
            team_a_row = [team_a_name]
            team_b_row = [team_b_name]
        results.append(Result(result_day, date, hour, team_a_row, team_b_row))
    return results


def get_days(c_id):
    url = f"https://www.voleibolib.net/JSON/get_combo_jornadas.asp?id={c_id}&fun=1"
    # fun parameter is mandatory, but its value can be 1 and 2. It only changes thet attributes inside the select.
    page = requests.get(url)
    soup = Bs(page.text, "html.parser")
    # In this case, the select has 2 option selected, the first one being a disabled, so I had to it this way
    options = [
        option["value"]
        for option in soup.find("select").find_all("option")
        if option["value"]
    ]
    return options
