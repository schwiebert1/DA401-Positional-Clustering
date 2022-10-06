# DA401-Positional-Clustering

### Introduction

Turner Schwiebert's Project for DA401 at Denison University (completed Fall 2022) first webscraped FBRef to collect physical and performance (per90) data on all football players in Europe's Top 5 Leagues (Premier League, Bundesliga, Ligue 1, Serie A, La Liga) for the past 365 days. Using this performance data, clustering algorithms were used analyze current positional roles in modern soccer. For more specific details on data acquisition and analysis methods, please read below.  

*STATUS:* offline

*DATA:* All data collected from: https://fbref.com/en/

## Files:

### fbref_srape.py:

***Overview:***

Scrapes player names from league's page. Uses that info to build valid URL's for each player. Collects per90 stats from each player's adavnced stats page. Compiles stats into data frames. Writes data frames to csv files.

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
      - Forwards (forwards.csv)
