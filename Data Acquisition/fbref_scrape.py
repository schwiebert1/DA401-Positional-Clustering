import os
import io
import requests
from lxml import etree
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm

# See README file for process overview, file descriptions, and data source

def getPlayerInfo(url, path="/Users/turnerschwiebert/Desktop/chromedriver"):

    driver = webdriver.Chrome(service=Service(path))
    driver.get(url)
    source_bytes = driver.page_source.encode()
    driver.quit()
    
    obj = io.BytesIO(source_bytes)
    htmltree = etree.parse(obj, parser=etree.HTMLParser())
    htmlroot = htmltree.getroot()
    
    names = htmlroot.xpath("""//*[@id="stats_standard"]/tbody/tr/td[1]/a/text()""")
    clubs = htmlroot.xpath("""//*[@id="stats_standard"]/tbody/tr/td[4]/a/text()""")
    
    player_names = []
    club_list = []
    for i in names:
        player_names.append(i.replace(" ", "-"))
    for i in clubs:
        club_list.append(i)
    assert len(player_names) == len(club_list)

    player_ids = []
    for element in htmlroot.xpath("""//*[@id="stats_standard"]/tbody/tr/td[1]/a"""):
        string = etree.tostring(element).decode()
        ID = string.split("""<a href="/en/players/""")[1][0:8]
        player_ids.append(ID)

    assert len(player_names) == len(player_ids)
    
    league = url.split("stats/")[1][:-6]
    if league.find("-") != -1:
        league = league.replace("-", " ")
    
    IDs = []
    for i in range(len(player_ids)):
        IDs.append((player_names[i], player_ids[i], league, club_list[i]))
        
    return IDs

def getPlayerRoot(info):
    if info[0].find("%") != -1: 
        return "Error"
    url = f"https://fbref.com/en/players/{info[1]}/scout/365_euro/{info[0]}-Scouting-Report"
    
    response = requests.get(url)
    
    obj = io.BytesIO(response.content)
    htmltree = etree.parse(obj, parser=etree.HTMLParser())
    htmlroot = htmltree.getroot()
    return htmlroot

def genAge(date, birth):
    #days_current = days + months*30 + years*365
    #not perfect but good enough!
    days_current = date[1] + date[0]*30 + date[2]*365

    #days_current = years*365 + months*30 + days
    days_at_birth = birth[0]*365 + birth[1]*30 + birth[2]

    age_days = days_current - days_at_birth
    age = age_days/365
    return age

def PlayerRow(root, info, date):
    
    #check root parameter
    if root == "Error":
        return "Error"
        
    row={}
    #make root a string
    rootSTR = etree.tostring(root).decode()
  
    #use 
    row['player_id'] = info[1]
    row ['name'] = info[0].replace("-"," ")
    row['club'] = info[3]
    row['league'] = info[2]

    #For fragile XPath variables, check for error. Error yields empty string
    try:
        #HEIGHT
        heightSTR = rootSTR.split("""cm</span>""")[0][-3:]
        row['height_cm'] = heightSTR
    except:
        row['height_cm'] = ""

    try:
        #WEIGHT
        weightSTR = rootSTR.split("""kg</span>""")[0][-3:]
        if weightSTR.find(">") != -1:
            weightSTR = weightSTR.split(">")[1]
        row['weight_kg'] = weightSTR
    except:
        row['weight_kg'] = ""

    try:
        #POSITION
        posSTR = rootSTR.split("vs. ")[1][:15]
        row['position'] = posSTR[:posSTR.find("s")]
    except:
        return "Error" #must return error if pos not found since pos needed for values...
            
    try:
        #PRIMARY FOOT
        footSTR = rootSTR.split("""Footed:</strong>""")[1][:20].split("% ")[1]
        row['foot'] = footSTR[:footSTR.find("<")]
    except:
        row['foot'] = ""
    
    try:
        #COUNTRY
        countrySTR = rootSTR.split("""National Team:</strong>""")[1].split(">")[1]
        row['country'] = countrySTR[:countrySTR.find("<")]
    except:
        row['country'] = ""

    try:
        #AGE
        # try:
        birthSTR = rootSTR.split("""id="necro-birth" data-birt""")[1].split("h=")[1][1:11]
        birth_date = birthSTR.split("-")
        birth = (int(birth_date[0]), int(birth_date[1]), int(birth_date[2]))
        #year, month, day
        age = round(genAge(date, birth), 2)
        row['age'] = age
        # except:
        #     print("Error - Age")
        #     quit()
    except:
        row['age'] = ""
    
    try:
        #PD_info  = "name - age - club"
        name = info[0].replace("-"," ")
        club = info[3]
        row['PD_Info'] = f"{name} - {age} - {club}"
    except:
        row['PD_Info'] = ""
    
    #ASSIGN "POS"
    pos = posSTR[:posSTR.find("s")]
    attrib = ""
    if pos == "Fullback":
        attrib = "FB"
    if pos == "Center Back":
        attrib = "CB"
    if pos == "Midfielder":
        attrib = "MF"
    if pos == "Forward":
        attrib = "FW"
    if pos == "Att Mid / Wing":
        attrib = "AM"
    # attrib used in format strings for xpath for outfield players
    
    #GOALKEEPERS:
    if pos == "Goalkeeper":
        vars = root.xpath(f"""//*[@id="scout_full_GK"]/tbody/tr/th/text()""")
        remove = [
            "Statistic",
            "Per 90",
            "Percentile",
            "Advanced Goalkeeping"
        ]
        vars = [i for i in vars if i not in remove]
        vals = root.xpath("""//*[@id="scout_full_GK"]/tbody/tr/td[1]/text()""")
        values = []
        for i in vals:
            if i.find("%") != -1:
                values.append(i[:-1])
            else:
                values.append(i)
    #NOT GOALKEEPERS:
    else:
        vars = root.xpath(f"""//*[@id="scout_full_{attrib}"]/tbody/tr/th/text()""")
        remove = [
            "Shooting",
            "Statistic",
            "Passing",
            "Pass Types",
            "Goal and Shot Creation",
            "Defense",
            "Possession",
            "Miscellaneous Stats",
            "Per 90",
            "Percentile"
        ]
        vars = [i for i in vars if i not in remove]

        vals = root.xpath(f"""//*[@id="scout_full_{attrib}"]/tbody/tr/td[1]/text()""")
        values = []
        for i in vals:
            if i.find("%") != -1:
                values.append(i[:-1])
            else:
                values.append(i)
    
    try:
        assert len(values) == len(vars)
    except:
        return "Error"
    
    if len(values) == 0:
        return "Error"
    
    tuples = []
    for i in range(len(values)):
        obj = (vars[i], float(values[i]))
        tuples.append(obj)
    
    for i in tuples:
        row[i[0]] = i[1]
    
    return [row, pos]

def getDate():
    response = requests.get("https://www.calendardate.com/todays.htm")
    date = response.text.split("""<td id="tprg"> """)[5].split("-")
    date_tuple = (int(date[0]), int(date[1]), int(date[2][:4]))
    return date_tuple

def genTables(date = getDate(),
    url_list = [
    "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "https://fbref.com/en/comps/13/stats/Ligue-1-Stats",
    "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "https://fbref.com/en/comps/12/stats/La-Liga-Stats"], 
    ):
    dest = os.getcwd() + "/../Data"
    
    prem_list = getPlayerInfo(url_list[0])
    ligue_list = getPlayerInfo(url_list[1])
    bundes_list = getPlayerInfo(url_list[2])
    serie_list = getPlayerInfo(url_list[3])
    liga_list = getPlayerInfo(url_list[4])
    
    info_list = prem_list + ligue_list + bundes_list + serie_list + liga_list
    
    player_list = []

    #ensures only unique players in df's
    found = set()
    for i in info_list:
        if i[1] not in found:
            player_list.append(i)
        found.add(i[1])
    
    FB_LoD = []
    CB_LoD = []
    MF_LoD = []
    FW_LoD = []
    GK_LoD = []
    for i in tqdm(player_list):
        result = PlayerRow(getPlayerRoot(i), i, date)
        if result[1] == "Error": # passes goalkeepers
            pass
        if result[1] == "Fullback":
            FB_LoD.append(result[0])
        if result[1] == "Center Back":
            CB_LoD.append(result[0])
        if result[1] == "Midfielder":
            MF_LoD.append(result[0])
        if result[1] == "Forward" or result[1] == "Att Mid / Wing":
            FW_LoD.append(result[0])
        if result[1] == "Goalkeeper":
            GK_LoD.append(result[0])
            
    FB_df = pd.DataFrame(FB_LoD)
    CB_df = pd.DataFrame(CB_LoD)
    MF_df = pd.DataFrame(MF_LoD)
    FW_df = pd.DataFrame(FW_LoD)
    GK_df = pd.DataFrame(GK_LoD)

    FB_df.to_csv(dest + "/fullbacks.csv")
    CB_df.to_csv(dest + "/centerbacks.csv")
    MF_df.to_csv(dest + "/midfielders.csv")
    FW_df.to_csv(dest + "/forwards.csv")
    GK_df.to_csv(dest + "/goalkeepers.csv")

    FULL_df = pd.concat([FB_df, CB_df, MF_df, FW_df]) #NOT GOALKEEPERS
    FULL_df.to_csv(dest + "/players.csv")

# FUNCTION CALL FOR COLLECTION:
genTables()

### TESTING ###

# getPlayerInfo ##

# premPlayers = getPlayerInfo("https://fbref.com/en/comps/9/stats/Premier-League-Stats")
# for i in premPlayers:
#     print(i)
# print("# of players: ", len(premPlayers))

## getPlayerRoot ##

# test_tuple = ('Brenden-Aaronson', '5bc43860', 'Premier League', 'Leeds United')
# rootSTR = etree.tostring(getPlayerRoot(test_tuple)).decode()
# print(rootSTR)

## PlayerRow ##

# Non-GK
# test_tuple = ('Brenden-Aaronson', '5bc43860', 'Premier League', 'Leeds United')
# today = getDate()
# print(PlayerRow(root = getPlayerRoot(test_tuple), info = test_tuple, date = today))

# GK
# test_tuple = ('Alisson', '7a2e46a8', 'Premier League', 'Liverpool')
# today = getDate()
# print(PlayerRow(root = getPlayerRoot(test_tuple), info = test_tuple, date = today))


## genAge / getDate ##

# print(getDate())
# print(genAge(getDate(), (2020, 1, 1)))