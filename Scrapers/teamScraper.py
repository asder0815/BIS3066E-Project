import io
import json
from os import error
import requests
from bs4 import BeautifulSoup

#urls to scrape
urls = []

#read urls
with open('teamurls.txt',"r") as f:
    urls = f.readlines()
    urls = [x.strip() for x in urls]
    f.close()

print(urls)

#json object for export
export = []

for url in urls: 
    try: 
        teamData = {
            'team': '',
            'winnings': '',
            'country' : '',
            'sponsors': [],
            'tournaments' : [], 
            'socials': []
        }
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        #get team name
        teamName = soup.find(class_='team-header').find('span', class_='title').text
        teamData['team'] = teamName
        #get team winnings
        headerDetails = soup.find(class_='header-details')
        teamWinnings = headerDetails.find_all(class_='header-details-detail')[0].find(class_='header-details-detail-subtitle').text.replace(" ", "").replace("$", "")
        teamData['winnings'] = teamWinnings
        #get country
        teamCountry = soup.find(class_='location').find('span').text
        teamData['country'] = teamCountry
        #get sponsors
        headers = headerDetails.find_all(class_='header-details-detail')
        for header in headers: 
            if 'Sponsors' in header.find(class_='header-details-detail-title').text:
                for sponsor in header.find(class_='header-details-detail-subtitle').find_all('span'): 
                    if not sponsor.text == '•':
                        teamData['sponsors'].append(sponsor.text)
                break
        #get tournaments
        tournamentTables = soup.find_all(class_='tournaments-one-block')

        for table in tournamentTables: 
            if 'tournament' in table.find(class_='tournaments-one-block-title').text:
                tournamentTableRows = table.find('tbody').find_all('tr')
                for row in tournamentTableRows: 
                    tournamentData = {
                        'name': '',
                        'viewers': ''
                    }
                    tableDatas = row.find_all('div', class_='table_refactored-data_primary')
                    print(tableDatas)
                    for data in tableDatas: 
                        if '$' not in data.text and '-' not in data.text:
                            tournamentData['viewers'] = data.text.replace(" ", "")
                            break
                    tournamentData['name'] = row.find(class_='table_refactored-data_primary cut_long_names').find('b').text
                    teamData['tournaments'].append(tournamentData)
                break
        #get socials
        #TODO: get social numbers
        print(teamData)
        export.append(teamData)
    except (error): 
        print('ERROR with ' + url)
        print(error)
with io.open('teamdata.json', 'w', encoding='utf-8') as outputfile:
    json.dump(export, outputfile, ensure_ascii=False, indent=4)