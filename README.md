# Scrapping voleibolib.net

Small app to scrap the [Illes Balears' volleyball federation website](https://www.voleibolib.net) and download the
results of each day and league and download it into `.csv` file. Also adds events to your calendar for each selected
league or team.

## Instalation

First, clone the project using the top right button or copy-pasting this into your terminal

```sh
git clone https://github.com/germanitxu/ScrapVoleibolIb.git
```

I recommend using a [virtual environment](https://docs.python.org/3/library/venv.html) to install the dependencies.

The `requirements.txt` file should list all Python libraries that the app depend on, and they will be installed using:

```sh
pip install -r requirements.txt
```

Finally, copy the [env.template](.env.template) into a new .env file

```sh
cp .env.template .env
```

## Google Credentials

As we are using google calendar services, you need to get API credentials.

1. [Create a new Google Cloud Platform (GCP) project](https://developers.google.com/workspace/guides/create-project)
2. [Configure the OAuth consent screen](https://developers.google.com/workspace/guides/configure-oauth-consent)
3. [Create a OAuth client ID credential](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)
   and download the `credentials.json`
4. Put downloaded `credentials.json` file into `~/google_creds/`directory.

On the first run, your application will prompt you to the default browser to get permissions from you to use your
calendar. Select the Google User you want to save the events on.

## Usage

### League selection

Using the command `leagues` will prompt the list of leagues currently ongoing and finished:

```sh
python main.py leagues
```

Use the **arrows key** to navigate and **space** to select the ones you want to save them for later use. You can use
this command again any time you want to update the leagues.

### Add calendar for leagues

If you have selected the leagues with the previous command, you can add events for each match of that league.

```sh
python main.py calendar_add_leagues
```

### Add calendar for specific teams

For each league you have selected, a prompt will show you a list of teams to save their matches as individual events on
the calendar.

```sh
python main.py calendar_add_teams
```

### Manual update

You can make this process manually by using the `update` command:

```sh
python main.py update
```

## Data

You can find the files under the `/data/` repository, which will be created after the first update. Inside `data` you
will find a folder for each league containing 2 files:

- `clasification_table.csv` Generic table with all teams and results
- `results_table.csv` each match with its results, ordered by date and hour

