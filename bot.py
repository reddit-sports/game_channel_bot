from urllib.request import urlopen
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
import datetime
import calendar
import collections
import discord
import logging


class Game_Channel_Bot:
    server_id = 356464812768886784
    category_id = 489221318978437120

    logging.basicConfig()
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    sched = AsyncIOScheduler()
    client = discord.Client()

    # Get games on script startup
    date = datetime.datetime.today()
    parameter = date.strftime('%Y%m%d')
    parameter = str(20180928) # This line is for testing purposes. Date is set to first day of preseason
    games = []
    format = '%H:%M %p'
    with urlopen('http://data.nba.com/prod/v2/' + parameter + '/scoreboard.json') as url:
        j = json.loads(url.read().decode())
        for game in j["games"]:
            gameDetails = {}
            gameDetails["time"] = datetime.datetime.strptime(game["startTimeEastern"].replace(" ET", ""), format).time()
            gameDetails["home"] = game["hTeam"]["triCode"]
            gameDetails["away"] = game["vTeam"]["triCode"]
            gameDetails['created_channel'] = False
            #print(gameDetails)
            games.append(gameDetails)


    # Method to update games daily
    async def update_games_daily(self):
        for game in self.games:
            try:
                game['channel'].delete()
            except Exception as e:
                print(e)
                pass
        date = datetime.datetime.today()
        parameter = date.strftime('%Y%m%d')
        parameter = str(20180928) # This line is for testing purposes. Date is set to first day of preseason
        self.games = []
        format = '%H:%M %p'
        with urlopen('http://data.nba.com/prod/v2/' + parameter + '/scoreboard.json') as url:
            j = json.loads(url.read().decode())
            for game in j["games"]:
                gameDetails = {}
                gameDetails["time"] = datetime.datetime.strptime(game["startTimeEastern"].replace(" ET", ""), format).time()
                gameDetails["home"] = game["hTeam"]["triCode"]
                gameDetails["away"] = game["vTeam"]["triCode"]
                gameDetails['created_channel'] = False
                #print(gameDetails)
                self.games.append(gameDetails)

    # Creates game thread channels
    async def create_game_threads(self):
        for game in self.games:
            # If it's one hour before the game and we haven't created a channel yet
            if (datetime.datetime.now() + datetime.timedelta(hours=1)).time() > game['time'] and game['created_channel'] == False:
                game['created_channel'] = True
            guild = self.client.get_guild(self.server_id)
            category = self.client.get_channel(self.category_id)
            channel = await guild.create_text_channel(game['away']+'-at-'+game['home'], category)
            game['channel'] = channel

    # Init - Adds jobs to scheduler
    def __init__(self):
        self.sched.add_job(self.update_games_daily, 'cron', hour=1)
        self.sched.add_job(self.create_game_threads, 'interval', minutes=1)
        self.sched.start()
        self.client.run('')
bot = Game_Channel_Bot()