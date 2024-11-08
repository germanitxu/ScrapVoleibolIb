# Scrapping voleibolib.net

Small app to scrap the [Illes Balears' volleyball federation website](https://www.voleibolib.net) and download the
results of each day and league and download it into `.csv` file. I needed this to avoid copy and pasting from the web
every single week.

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

## How to use it

### League selection
Using the command `leagues` will prompt the list of leagues currently ongoing and finished:
```sh
python main.py leagues
```
Use the **arrows key** to navigate and **space** to select the ones you want to download the available results. Once you have
selected the desired leagues, it will ask you whether to create a cron (not available on Windows systems right now) to 
download the leagues every monday.

You can use this command again any time you want to update the leagues and cron cofiguration.

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

