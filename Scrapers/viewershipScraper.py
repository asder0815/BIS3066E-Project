import io
import json
from os import error
import requests
from bs4 import BeautifulSoup

#urls to scrape
#example: https://escharts.com/tournaments/lol/lcs-2021-summer
urls = []

#read urls
with open('./../../viewrshipurls.txt',"r") as f:
    urls = f.readlines()
    urls = [x.strip() for x in urls]
    f.close()

print(urls)

#json object for export
export = []

for url in urls: 
    try: 
        tourneyData = {
            'tournament': url,
            'matches': []
        }   
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find(id='popular-matches')
        matches = table.find_all('div', class_='versus-block matches-data')
        for match in matches: 
            if match.has_attr('data-filter') and match['data-filter'] == 'total':
                matchdata = {}
                teams = match.find_all('a', class_='name')
                teamString = ''
                teamCounter = 0
                for team in teams:
                    if(teamCounter != 0):
                        teamString = teamString + '|' + team.text.strip()
                    else: 
                        teamString = teamString + team.text.strip()
                    teamCounter = teamCounter + 1
                matchdata['teams'] = teamString
                details = match.find(class_='versus-block-details')
                viewers = details.find(class_='title').text.replace(" ", "")
                matchdata['viewers'] = viewers
                tourneyData['matches'].append(matchdata)
        print(tourneyData)
        export.append(tourneyData)
    except (error): 
        print('ERROR with ' + url)
        print(error)
with io.open('./src/assets/viewershipdata.json', 'w', encoding='utf-8') as outputfile:
    json.dump(export, outputfile, ensure_ascii=False, indent=4)
