from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

def load_all_matches(driver, time_sleep):
    '''
    This function go to the bottom of the page, click the button to load all matches and finnaly go back to the top of the page when all matches are loaded
    '''
    while True:
        # scroll down and show other matches
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(time_sleep)
            driver.find_element(By.LINK_TEXT, 'Pokaż więcej meczów').click()
            time.sleep(time_sleep)
        except:
            driver.execute_script("window.scrollTo(0, 200);")
            time.sleep(time_sleep)
            break


def get_matches(season):

    # go to the page of the season we are looking for
    if season == '2022-2023':
        flashscore_url = "https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa/wyniki/"
    else:
        flashscore_url = f"https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa-{season}/wyniki/"

    # load all matches
    driver = webdriver.Chrome()
    driver.get(flashscore_url)
    driver.set_window_size(1120, 1000)

    # reject cookies
    try:
        cookies_button = driver.find_element(By.ID,'onetrust-reject-all-handler')
        cookies_button.click()
    except:
        print()

    load_all_matches(driver,0.4)
    matches = []
    # find all matches
    match_buttons = driver.find_elements(By.CLASS_NAME, "event__match--twoLine")
    # in the season 2012-2013 we have statistics only for last 111 matches
    if season == '2012-2013':
        match_buttons = match_buttons[0:112]
    # get number of goals for all matrches from main page and convert to DataFrames (will join them at the end to dataframe with all
    # statistics from each match)
    goals_home = driver.find_elements(By.CLASS_NAME, 'event__score--home')
    goals_away = driver.find_elements(By.CLASS_NAME, 'event__score--away')
    goals_home = pd.DataFrame(goals_home)
    goals_home.iloc[:, 0] = goals_home.iloc[:, 0].apply(lambda x: x.text)
    goals_home.columns = ['goals_home']
    goals_away = pd.DataFrame(goals_away)
    goals_away.iloc[:,0] = goals_away.iloc[:,0].apply(lambda x: x.text)
    goals_away.columns = ['goals_away']

    # going through each match in this page
    for match in match_buttons:
        print("Progress: {}".format("" + str(len(matches))) + "/" + str(len(match_buttons)) + ' season' + season)
        driver.execute_script("window.scrollBy(0, 53);")
        time.sleep(0.5)

        # open window with a single match
        match.click()
        # switch to window with a single match
        driver.switch_to.window(driver.window_handles[1])
        # switch to stats
        stats_button = driver.find_element(By.LINK_TEXT, 'STATYSTYKI')
        stats_button.click()
        time.sleep(0.5)

        # get all stats from each match
        all_stats_home = driver.find_elements(By.CLASS_NAME, "stat__homeValue")
        all_stats_category = driver.find_elements(By.CLASS_NAME, "stat__categoryName")
        all_stats_away = driver.find_elements(By.CLASS_NAME, "stat__awayValue")

        stats_home = []
        stats_away = []

        # get team names, date, number of round and number of goals
        team_names = driver.find_elements(By.CLASS_NAME, "participant__participantName")
        date = driver.find_element(By.CLASS_NAME,'duelParticipant__startTime').text
        round = driver.find_element(By.PARTIAL_LINK_TEXT, 'KOLEJKA').text[-2:]

        # get value for each stat for both teams
        for i in range(0, len(all_stats_home)):
            stats_home.append(all_stats_home[i].text)
            stats_away.append(all_stats_away[i].text)
        print(stats_home)
        print(len(stats_home))
        print(stats_away)

        # add all stats
        dict = {
                "Season": season,
                "Round" : round,
                "Date" : date,
                "Team_Home" : team_names[0].text,
                "Team_Away" : team_names[-1].text
                }
        keys = range(0,len(all_stats_category))
        for i in keys:
            dict[all_stats_category[i].text + '_home'] = all_stats_home[i].text
            dict[all_stats_category[i].text + '_away'] = all_stats_away[i].text
        matches.append(dict)


        # matches.append({
        #                 "Season" : season,
        #                 "Home Team": stats_home[0],
        #                 "ball_posession_home": stats_home[1],
        #                 "goal_situations_home": stats_home[2],
        #                 "shots_on_target_home": stats_home[3],
        #                 "shots_no_target_home": stats_home[4],
        #                 "blocked_shots_home": stats_home[5],
        #                 "free_kicks_home": stats_home[6],
        #                 "corners_home": stats_home[7],
        #                 "offsides_home": stats_home[8],
        #                 "auts_home": stats_home[9],
        #                 "interventions_home": stats_home[10],
        #                 "fauls_home": stats_home[11],
        #                 "red_cards_home": stats_home[12],
        #                 "yellow_cards_home": stats_home[13],
        #                 "passes_home": stats_home[14],
        #                 "passes_target_home": stats_home[15],
        #                 "blocks_home": stats_home[16],
        #                 "attacks_home": stats_home[17],
        #                 "dang_attacks_home": stats_home[18],
        #                 "Away Team": stats_away[0],
        #                 "ball_posession_away": stats_away[1],
        #                 "goal_situations_away": stats_away[2],
        #                 "shots_on_target_away": stats_away[3],
        #                 "shots_no_target_away": stats_away[4],
        #                 "blocked_shots_away": stats_away[5],
        #                 "free_kicks_away": stats_away[6],
        #                 "corners_away": stats_away[7],
        #                 "offsides_away": stats_away[8],
        #                 "auts_away": stats_away[9],
        #                 "interventions_away": stats_away[10],
        #                 "fauls_away": stats_away[11],
        #                 "red_cards_away": stats_away[12],
        #                 "yellow_cards_away": stats_away[13],
        #                 "passes_away": stats_away[14],
        #                 "passes_target_away": stats_away[15],
        #                 "blocks_away": stats_away[16],
        #                 "attacks_away": stats_away[17],
        #                 "dang_attacks_away": stats_away[18]
        #                 })
        # close match window
        driver.close()
        # go back to window with all matches
        driver.switch_to.window(driver.window_handles[0])
    df = pd.DataFrame(matches)
    # merge dataframes with goals
    df = df.join(goals_home).join(goals_away)
    file_name = season + '.csv'
    df.to_csv(file_name, encoding='utf-8')
    driver.close()


# get all data from seasons where we have statistics for matches (from last 111 matches of season 2012/2013)
for i in range(2018,2023):
    print(f'{str(i)}-{str(i+1)}')
    get_matches(f'{str(i)}-{str(i+1)}')
