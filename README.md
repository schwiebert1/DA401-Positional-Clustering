# DA401-Positional-Clustering

### Introduction

Turner Schwiebert's Project for DA401 at Denison University (completed Fall 2022) first webscraped FBRef to collect physical and performance (per90) data on all football players in Europe's Top 5 Leagues (Premier League, Bundesliga, Ligue 1, Serie A, La Liga) for the past 365 days. Using this performance data, clustering algorithms were used to identify current positional roles in modern soccer. For more specific details on data acquisition and analysis methods, please read below.  

All data collected from: https://fbref.com/en/

## Data Acquisition:

### fbref_srape.py:

***Overview:***

Scrapes player names from league's page. Uses that info to build valid URL's for each player. Collects per90 stats from each player's adavnced stats page. Compiles stats into data frames. Writes data frames to csv files. 

The run time for this file was about 56 minutes on my MacBook. This file requires Google Chrome installed and an up to date Google Chrome webdriver, which can be found here: https://chromedriver.chromium.org/downloads

***Functions:***

  - getPlayerInfo: Returns list of player names, club, league, and FBRef player ID by scraping league page (using chrome web driver)
  - getPlayerRoot: Builds player-specific url and returns its parsed html response (root)
  - genAge: returns up-to-date age using birth day and runtime's date (invoked in PlayerRow)
  - PlayerRow: does XPath heavy lifting. Returns list [row, pos] where row is a dict with many variables/values and pos is player's field position
  - getDate: scrapes today's date from https://www.calendardate.com/todays.htm, returns date as tuple
  - genTables: uses pandas to turn rows from PlayerRow into data frames and writes csv files for
      - All positions (players.csv)
      - Fullbacks (fullbacks.csv)
      - Centerbacks (centerbacks.csv)
      - Midfielders (midfielders.csv)
      - Forwards/Att Mids & Wingers (forwards.csv)
      
### Data

As written above, "fbref_scrape.py" outputs 5 csv files. These are saved in the Data folder under Data Acquisition. 
The webscraper was last run on October 20th, 2022. For reproducibility of results of this study, these data sets have been renamed from the raw output name. If the webscraper is run, it will output new csv files that do not overwrite the data used for analysis. 
- All positions (players10_20_2022.csv)
- Fullbacks (fullbacks10_20_2022.csv)
- Centerbacks (centerbacks10_20_2022.csv)
- Midfielders (midfielders10_20_2022.csv)
- Forwards/Att Mids & Wingers (forwards10_20_2022.csv)

## Positional Analysis:

### phase1.Rmd

Contains phase 1 of this research project: analysis of positional roles using all FBRef performance data pooled together. See "Methods" section of the Final Paper for more details.
There is no outut for this .Rmd file. 

### phase2.Rmd

Contains phase 2 of this research project: analysis of positional roles using FBRef performance data broken up by traditional positions as defined by FBRef. 
These positions include Forwards, Attacking Midfielders/Wingers, Midfielders, Fullbacks, and Center Backs. 
This file outputs the actual clusters contained in the "Clusters" folder of the "Analysis" folder. For more information on the findings contained in these clusters, run this file and see the Results and Discussion section of the Final Paper. 


