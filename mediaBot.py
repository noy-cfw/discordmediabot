import discord
import json 
import requests

# Discord Token
TOKEN = ''

# Radarr Info
rKey = ''
rApi = ''
rEndpoints = {
    'Calendar': '/calendar',
    'Command': '/command',
    'Diskspace': '/diskspace',
    'History': '/history',
    'Movie': '/movie',
    'Movie-Lookup': '/movie/lookup',
    'Queue': '/queue',
    'System-Status': '/system/status',
}

# Sonarr Info
sKey = ''
sApi = ''
sEndpoints = {
    'Calendar': '/calendar',
    'Command': '/command',
    'Diskspace': '/diskspace',
    'Episode': '/episode',
    'EpisodeFile': '/episodefile',
    'History': '/history',
    'Images': '/MediaCover',
    'Wanted Missing': '/wanted/missing/',
    'Queue': '/queue',
    'Parse': '/parse',
    'Profile': '/profile',
    'Release': '',
    'Release/Push': '',
    'Rootfolder': '/rootfolder',
    'Series': '/series',
    'Series-Lookup': '/series/lookup',
    'System-Status': '/system/status',
    'System-Backup': '/system/backup',
    'Tag': '/tag'
}


class rSearch:

    # Accept movie name in array form, and search type('byTerm' or 'byId')
    def __init__(self, name, sType): 
        self.name = name
        self.sType = sType
        self.title = None
        self.year = None
        self.dLoad = None
        self.tmdbId = None
        self.iUrl = None
        self.titleSlug = None
        self.rImgArray = None
        self.__radarrSearch()


    def __radarrSearch(self):

        searchtype = ''
        searchterm = ''
        
        # If searching by id, the json response doesn't return an array
        # so need to have two separate parsing actions
        isArray = False

        # Set search type
        if self.sType == 'byTerm':
            searchtype = '?term='
            isArray = True 
            # Format the search term  eg. harry%20potter%20               
            for i in self.name:         
                searchterm += i + '%20'
        elif self.sType == 'byId':
            searchtype = '/tmdb?tmdbId='  
            searchterm = self.name[0]

        # Query Server
        qResponse = requests.get(rApi+rEndpoints['Movie-Lookup']+searchtype+searchterm+'&apikey='+rKey) 
        # Convert qResponse to json
        jResponse = qResponse.json()
        if isArray:
            # Grab first json object info
            self.title = str((jResponse[0])["title"])
            self.year = year = str((jResponse[0])["year"])
            self.dLoad = str((jResponse[0])["downloaded"])
            self.tmdbId = str((jResponse[0])["tmdbId"])
            self.rImgArray = ((jResponse[0])["images"])
            self.iUrl = str(self.rImgArray[0]["url"])
            self.titleSlug = str(jResponse[0]["titleSlug"])
        elif (not isArray):
            self.title = str((jResponse)["title"])
            self.year = year = str((jResponse)["year"])
            self.dLoad = str((jResponse)["downloaded"])
            self.tmdbId = str((jResponse)["tmdbId"])
            self.rImgArray = ((jResponse)["images"])
            self.iUrl = str(self.rImgArray[0]["url"])
            self.titleSlug = str(jResponse["titleSlug"])

class sSearch:

    # Accept show name in array form, search type('byTerm' or 'byId'), and show type('tv' or 'anime')
    def __init__(self, name, scType, shType):
        self.name = name
        self.scType = scType
        self.shType = shType
        self.title = None
        self.year = None
        self.dLoad = None
        self.tvdbId = None
        self.iUrl = None
        self.titleSlug = None
        self.rImgArray = None
        self.seasons = None
        self.seasonCount = None
        self.__sonarrSearch()

    def __sonarrSearch(self):

        searchtype = ''
        searchterm = ''
        
        # Set search type
        if self.scType == 'byTerm':
            searchtype = '?term='
            # Format the search term  eg. harry%20potter%20               
            for i in self.name:         
                searchterm += i + '%20'
        elif self.scType == 'byId':
            searchtype = '?term=tvdb:'  
            searchterm = self.name[0]

        # Query Server
        qResponse = requests.get(sApi+sEndpoints['Series-Lookup']+searchtype+searchterm+'&apikey='+sKey) 
        # Convert qResponse to json
        jResponse = qResponse.json()

        # Grab first json object info
        self.title = str((jResponse[0])["title"])
        self.year = year = str((jResponse[0])["year"])
        self.tvdbId = str((jResponse[0])["tvdbId"])
        self.rImgArray = ((jResponse[0])["images"])
        self.iUrl = str(self.rImgArray[1]["url"])
        self.titleSlug = str(jResponse[0]["titleSlug"])
        self.seasonCount = str(jResponse[0]["seasonCount"])
        self.seasons = (jResponse[0]["seasons"])

client = discord.Client()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    txtmessage = message.content

    if txtmessage[:9] == '!addmovie':
        try:
            # Check for basic syntax
            splitmsg = txtmessage.split()
            if len(splitmsg) == 1 or len(splitmsg[0]) > 9 or len(splitmsg) > 2:
                await message.channel.send('Incorrect Syntax, use !addmovie {TMDB ID}')
            splitmsg.remove('!addmovie')

            # Create new instance of rSearch with byId option
            ma = rSearch(splitmsg, 'byId')

            # Set Some Extra Params for POST
            qualityProfileId = 1
            profileId = 1
            path = "/movies/"

            data = {
                "title": ma.title,
                "qualityProfileId": qualityProfileId,
                "titleSlug": ma.titleSlug,
                "images": ma.rImgArray,
                "tmdbId": ma.tmdbId,
                "profileId": profileId,
                "year": ma.year,
                "rootFolderPath": path,
                "addOptions" : {
                    "searchForMovie" : True
                }
            } 
            payload = requests.post(rApi+rEndpoints['Movie']+'?apikey='+rKey, data = json.dumps(data)) 
            await message.channel.send('Adding and downloading ' + ma.title)
        except:
            await message.channel.send('Something went wrong, check your syntax or TMDB ID')

    # Movie Search Command       
    if txtmessage[:12] == '!searchmovie':
        try:
            # Check basic syntax
            splitmsg = txtmessage.split()
            if len(splitmsg) == 1 or len(splitmsg[0]) > 12:
                await message.channel.send('Incorrect Syntax, use !searchmovie <Movie title>')
            splitmsg.remove('!searchmovie')

            # Create new instance of rSearch with byTerm option
            ms = rSearch(splitmsg, 'byTerm')

            # Embed Search Result Message
            embed=discord.Embed(title="Search Results ")
            embed.set_thumbnail(url=ms.iUrl)
            embed.add_field(name=ms.title, value="Year: "+ms.year+" | Downloaded: "+ms.dLoad+" | TMDB ID: "+ms.tmdbId, inline=False)
            embed.set_footer(text="Use '!addmovie "+ms.tmdbId+ "' to add movie to server")
            await message.channel.send(embed=embed)

        except:
            await message.channel.send('Search failed, try different terms')

    # TV Show Search Command
    if txtmessage[:13] == '!searchtvshow':
        try:
            # Check basic syntax
            splitmsg = txtmessage.split()
            if len(splitmsg) == 1 or len(splitmsg[0]) > 13:
                await message.channel.send('Incorrect Syntax, use !searchmovie <TV Show>')
            splitmsg.remove('!searchtvshow')
            
            ts = sSearch(splitmsg, 'byTerm', 'tv')

            # Embed Search Result Message
            embed=discord.Embed(title="Search Results ")
            embed.set_thumbnail(url=ts.iUrl)
            embed.add_field(name=ts.title, value="Year: "+ts.year+" | TVDB ID: "+ts.tvdbId, inline=False)
            embed.set_footer(text="Use '!addtvshow "+ts.tvdbId+ "' to add show to server")
            await message.channel.send(embed=embed)

        except:
            await message.channel.send('Search failed, try different terms')

    # TV Show Add Command 
    if txtmessage[:10] == '!addtvshow':
        try:
            # Check basic syntax
            splitmsg = txtmessage.split()
            if len(splitmsg) == 1 or len(splitmsg[0]) > 13:
                await message.channel.send('Incorrect Syntax, use !searchmovie <TV Show>')
            splitmsg.remove('!addtvshow')
            
            ts = sSearch(splitmsg, 'byId', 'tv')



           # Set Some Extra Params for POST
            profileId = 1
            path = "/tv/"


            data = {
                "title": ts.title,
                "titleSlug": ts.titleSlug,
                "images": ts.rImgArray,
                "tvdbId": ts.tvdbId,
                "profileId": profileId,
                "seasons": ts.seasons,
                "rootFolderPath": path,
                "addOptions" : {
                    "ignoreEpisodesWithFiles": True,
                    "ignoreEpisodesWithoutFiles": False,
                    "searchForMissingEpisodes": True
                }
            } 

            payload = requests.post(sApi+sEndpoints['Series']+'?apikey='+sKey, data = json.dumps(data)) 

            await message.channel.send('Adding and downloading ' + ts.title)
        except:
            await message.channel.send('Something went wrong, check your syntax or TVDB ID')


    # Anime Search Command 
    if txtmessage[:12] == '!searchanime':
        try:
            # Check basic syntax
            splitmsg = txtmessage.split()
            if len(splitmsg) == 1 or len(splitmsg[0]) > 12:
                await message.channel.send('Incorrect Syntax, use !searchanime <Show>')
            splitmsg.remove('!searchanime')
            
            ans = sSearch(splitmsg, 'byTerm', 'anime')


            embed=discord.Embed(title="Search Results ")
            embed.set_thumbnail(url=ans.iUrl)
            embed.add_field(name=ans.title, value="Year: "+ans.year+" | TVDB ID: "+ans.tvdbId, inline=False)
            embed.set_footer(text="Use '!addanime "+ans.tvdbId+ "' to add show to server")
            await message.channel.send(embed=embed)

        except:
            await message.channel.send('Search failed, try different terms')

    # Anime Add Command 
    if txtmessage[:9] == '!addanime':
        try:
            # Check basic syntax
            splitmsg = txtmessage.split()
            if len(splitmsg) == 1 or len(splitmsg[0]) > 12:
                await message.channel.send('Incorrect Syntax, use !searchanime <Show>')
            splitmsg.remove('!addanime')
            
            ans = sSearch(splitmsg, 'byId', 'anime')


           # Set Some Extra Params for POST
            profileId = 1
            path = "/anime/"
            
            data = {
                "title": ans.title,
                "titleSlug": ans.titleSlug,
                "images": ans.rImgArray,
                "tvdbId": ans.tvdbId,
                "profileId": profileId,
                "seasons": ans.seasons,
                "rootFolderPath": path,
                "addOptions" : {
                    "ignoreEpisodesWithFiles": True,
                    "ignoreEpisodesWithoutFiles": False,
                    "searchForMissingEpisodes": True
                }
            } 


            payload = requests.post(sApi+sEndpoints['Series']+'?apikey='+sKey, data = json.dumps(data)) 

            await message.channel.send('Adding and downloading ' + ans.title)
        except:
            await message.channel.send('Something went wrong, check your syntax or TVDB ID')
    
client.run(TOKEN)

