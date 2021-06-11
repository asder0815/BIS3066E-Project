import io
import json
import requests
from bs4 import BeautifulSoup

#urls to scrape
#example: https://lol.fandom.com/wiki/LEC/2020_Season/Spring_Playoffs
urls = []

#read urls
with open('./../../tournamenturls.txt',"r") as f:
    urls = f.readlines()
    urls = [x.strip() for x in urls]
    f.close()

print(urls)

#json object for export
export = []

tourneylist= []

for url in urls:
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        tables = soup.find('table', class_='wikitable2 tournament-results zebra-manual')
        result = []
        headerdict = {}
        lastheader = ''
        for table in tables: 
                headers = table.find_all('th')
                headercount = 0
                for header in headers: 
                    headercount += 1
                    headerdict[str(headercount)] = str(headercount) + "_" + header.text.strip()
                    lastheader = str(headercount) + "_" + header.text.strip()
                rows = table.find_all('tr')
                specialrows = []
                specialrowaddto = 0
                rowcounter = 0
                rowiteration = 0
                for row in rows: 
                    rowiteration +=1 
                    if not rowiteration in specialrows:
                        rowcounter += 1
                        dataset = {}
                        cells = row.find_all('td')
                        cellcount = 0
                        for cell in cells: 
                            cellcount += 1
                            if cellcount == 1 and cell.has_attr('rowspan') and int(cell['rowspan']) > 1: 
                                specialrowaddto = rowcounter
                                i = rowiteration + 1
                                for i in range (rowiteration, rowiteration + int(cell['rowspan'])):
                                    specialrows.append(i)
                                    i += 1
                            dataset[headerdict[str(cellcount)]] = [(cell.text.strip().encode('ascii', 'ignore')).decode("utf-8").replace(' ', '').replace('\n', '').replace('\r', '')]
                        result.append(dataset)
                    else: 
                        cell = row.find('td')
                        dataset = result[specialrowaddto - 1]
                        dataset[lastheader].append((cell.text.strip().encode('ascii', 'ignore')).decode("utf-8").replace(' ', '').replace('\n', '').replace('\r', ''))
                export.append({url: result})
        tourneylist.append(url[27:])
    except: 
        print('ERROR with ' + url)

cleanedData = []
for tourney in tourneylist: 
    print(tourney); 
    tourneyresult = {tourney: []}
    urlname = ''
    for url in urls: 
        if tourney in url:
            urlname = url
    if not urlname == '': 
        correctset = {}
        for data in export: 
            if urlname in data.keys():
                correctset = data[urlname]
        if not data == {}:
            for result in correctset:
                dataset = {}
                for attribute in result.keys():
                    if 'Place' in attribute: 
                        dataset['place'] = result[attribute][0]
                    if 'Prize' in attribute and not '%' in attribute: 
                        dataset['price'] = result[attribute][0]
                    if 'Team' in attribute: 
                        teamstring = ''
                        teamcounter = 0
                        for team in result[attribute]: 
                            teamcounter += 1
                            if teamcounter < len(result[attribute]):
                                teamstring = teamstring + str(team) + '|'
                            else: 
                                teamstring = teamstring + str(team)
                        dataset['teams'] = teamstring
                tourneyresult[tourney].append(dataset)
    cleanedData.append(tourneyresult)

with io.open('./src/assets/tournamentdata.json', 'w', encoding='utf-8') as outputfile:
    json.dump(cleanedData, outputfile, ensure_ascii=False, indent=4)