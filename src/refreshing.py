import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from unidecode import unidecode
import os
from dotenv import load_dotenv
from constants import DATA_PATHS

load_dotenv()

BASE_URL = "https://www.basketball-reference.com/leagues/"

api_key = os.getenv('API_KEY')
sportsbook = os.getenv('SPORTSBOOK')
league = os.getenv('LEAGUE')

def get_box_score_links(year : int, month : str, headers : dict):
    """
    Retrieves list of box score links found within a month on basketball-reference.com.

    Parameters:
        year (int): Year of month.
        month (str): ID for month.
        headers (dict): object containing headers for requests
    """
    time.sleep(3)
    month_url = f"{BASE_URL}NBA_{year}_games-{month}.html"
    print(f"Scraping: {month_url}")
    response = requests.get(month_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    box_score_links = []
    for a_tag in soup.find_all('a', string="Box Score"):
        box_score_url = urljoin(BASE_URL, a_tag['href'])
        box_score_links.append(box_score_url)
    return box_score_links

def get_player_stats(box_score_url : str, headers : dict):
    """
    Uses a box score URL from get_box_score_links() to retrieve
    combined basic-advanced box score stats for both teams in one game.

    Parameters:
        box_score_url (str): URL to pass through requests.get().
        headers (dict): object containing headers for requests
    """
    time.sleep(3)
    response = requests.get(box_score_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content.decode("utf-8"), 'html.parser')
    tabs = soup.select('table[id*="-game-basic"], table[id*="-game-advanced"]')
    team_stats = {"basic": {}, "advanced": {}}
    for tab in tabs:
        cols, players = [], []
        table_id = tab['id']
        table_type = "basic" if "basic" in table_id else "advanced"
        team = table_id.split('-')[1]
        for s in tab.select('thead tr:nth-child(2) th'):
            cols.append(s.text)
        for j in tab.select('tbody tr, tfoot tr'):
            player = [data.text for data in j.select('td,th')]
            players.append(player)
        max_length = len(max(players, key=len))
        players_plus = [player + [""] * (max_length - len(player)) for player in players]
        df = pd.DataFrame(players_plus, columns=cols)
        if team not in team_stats[table_type]:
            team_stats[table_type][team] = df
        else:
            team_stats[table_type][team] = pd.concat([team_stats[table_type][team], df], ignore_index=True)
    combined_stats = {}
    for team in team_stats["basic"]:
        if team in team_stats["advanced"]:
            basic_df = team_stats["basic"][team]
            advanced_df = team_stats["advanced"][team]
            duplicate_cols = set(basic_df.columns).intersection(set(advanced_df.columns)) - {"Starters"}
            advanced_df = advanced_df.drop(columns=list(duplicate_cols), errors="ignore")
            combined_df = pd.merge(basic_df, advanced_df, on="Starters", how="outer")
        else:
            combined_df = team_stats["basic"][team]
        combined_df["Team"] = team
        combined_stats[team] = combined_df
    all_stats_combined = pd.concat(combined_stats.values(), ignore_index=True)
    game_id = box_score_url.split('/')[-1].replace('.html', '')
    all_stats_combined["GameID"] = game_id
    return all_stats_combined

def get_player_props(api_key : str, sportsbook : str, league : str):
    """
    Uses dailyfantasyapi to retrieve upcoming odds lines for the NBA

    Parameters:
        api_key (str) : free API key for dailyfantasyapi to allow calls
        sportsbook (str) : name of sportsbook for api request (i.e. PrizePicks)
        league (str) : name of league to pull upcoming lines from
    """
    url = "https://api.dailyfantasyapi.io/v1/lines/upcoming"
    headers = {"x-api-key": api_key}
    params = {
        "sportsbook": sportsbook,
        "league": league,
        "is_available": 'true'
    }
    response = requests.get(url, headers=headers, params=params)
    print(f"Response Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            return data
        else:
            return None
    else:
        print(f"Error: {response.status_code}, Response: {response.text}")
        return None

def process_player_props(data : str):
    """
    Processes entire dailyfantasyapi response JSON into pandas dataframe for analysis

    Parameters:
        data (str) : JSON containing upcoming odds from get_player_props()
    """
    records = []
    for item in data:
        line_id = item.get('line_id', 'Unknown')
        game_id = item.get('game_id', 'Unknown')
        players = item.get('players', [])
        line = item.get('line', 'Unknown')
        market = item.get('market', 'Unknown')
        league = item.get('league', 'Unknown')
        is_available = item.get('is_available', False)
        sportsbook = item.get('sportsbook', 'Unknown')
        game_date = item.get('game_date', 'Unknown')
        start_time = item.get('start_time', 'Unknown')
        grade = item.get('grade', 'Unknown')
        line_changes = item.get('line_changes', [])
        for player in players:
            records.append({
                "Line ID": line_id,
                "Game ID": game_id,
                "Player Name": player.get('name', 'Unknown'),
                "Normalized Name": player.get('normalized_name', 'Unknown'),
                "Team": player.get('team', 'Unknown'),
                "Line": line,
                "Market": market,
                "League": league,
                "Is Available": is_available,
                "Sportsbook": sportsbook,
                "Game Date": game_date,
                "Start Time": start_time,
                "Grade": grade,
                "Line Changes": line_changes
            })
    return records

def get_latest_game_date(processed_file_path: str) -> tuple[int, str]:
    """
    Reads the processed NBA data file and returns the most recent game date.
    
    Parameters:
        processed_file_path (str): Path to the processed NBA data CSV
    
    Returns:
        tuple: (year, month) of the most recent game
    """
    try:
        df = pd.read_csv(processed_file_path)
        df['date'] = pd.to_datetime(df[['Year', 'Month', 'Day']])
        latest_date = df['date'].max()
        return latest_date.year, latest_date.strftime('%B').lower()
    except FileNotFoundError:
        # If file doesn't exist, return default start date
        return 2024, 'october'

def get_remaining_months(current_month: str, all_months: list) -> list:
    """
    Returns list of months to scrape starting from current month.
    
    Parameters:
        current_month (str): Month to start from
        all_months (list): Full list of NBA season months
    
    Returns:
        list: Remaining months to scrape
    """
    try:
        current_idx = all_months.index(current_month)
        return all_months[current_idx:]
    except ValueError:
        return all_months

def dataset_refresh():
    """
    Recallable function that runs data retrieval for both box score
    stats and odds, allows users to retrieve new data.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    # Get the latest game date from existing data
    current_year, current_month = get_latest_game_date(DATA_PATHS['PROCESSED_NBA'])
    months = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
    months_to_scrape = get_remaining_months(current_month, months)
    
    # Load existing data if available
    try:
        all_player_stats = pd.read_csv(DATA_PATHS['RAW_NBA'])
    except FileNotFoundError:
        all_player_stats = pd.DataFrame()
    
    # Scrape new box score data
    for month in months_to_scrape:
        box_score_links = get_box_score_links(current_year, month, headers)
        for box_score_url in box_score_links:
            game_id = box_score_url.split('/')[-1].replace('.html', '')
            # Skip if game already exists in dataset
            if not all_player_stats.empty and game_id in all_player_stats['GameID'].values:
                continue
            game_stats = get_player_stats(box_score_url, headers)
            all_player_stats = pd.concat([all_player_stats, game_stats], ignore_index=True)
    
    # Save updated raw data
    all_player_stats.to_csv(DATA_PATHS['RAW_NBA'], index=False)
    
    # Get and save player props data
    api_key = "5f1276c7-b5c5-40f9-9412-ed61622eb599"
    sportsbook = "PrizePicks"
    league = "NBA"
    
    # Fetch player props
    props_data = get_player_props(api_key, sportsbook, league)
    if props_data:
        records = process_player_props(props_data)
        if records:
            props_df = pd.DataFrame(records)
            props_df.to_csv(DATA_PATHS['PLAYER_PROPS'], index=False)
        else:
            print("No player props records to save.")
    else:
        print("Failed to retrieve player props data.")


def column_fixing(df : pd.DataFrame):
    """
    Fixes column names (Starters -> Players)
    Removes players that did not play in the games they're included in
    Ensure columns are correct type

    Parameters:
        df (pd.DataFrame) : dataframe containing raw current NBA season box score statistics
    """
    if "Starters" in df.columns:
        df.rename(columns={"Starters": "Player"}, inplace=True)
    df['MP'] = df['MP'].replace(['Did Not Dress', 'Did Not Play', 'Not With Team', 'Player Suspended'], 'DNP')
    df = df[df["Player"] != "Reserves"]
    df = df[df["Player"] != "Team Totals"]
    df = df[df['MP'] != 'DNP']
    df['PTS'] = df['PTS'].astype(float)
    df['Player'] = df['Player'].apply(unidecode)
    return df

def type_change(df : pd.DataFrame):
    """
    Fixes column names (Starters -> Players)
    Removes players that did not play in the games they're included in
    Ensure columns are correct type

    Parameters:
        df (pd.DataFrame) : dataframe containing raw current NBA season box score statistics
    """
    def mp_to_seconds(mp : str):
        """
        Function for apply()
        Takes an MP string value and changes it into an integer of seconds from minutes

        Parameters:
            mp (str) : string representing minutes:seconds played
        """
        if ':' in mp:
            minutes, seconds = map(int, mp.split(':'))
            return minutes * 60 + seconds
        elif mp == "DNP":
            return 0
        return mp
    df['MP'] = df['MP'].apply(mp_to_seconds)
    df['MP'] = df['MP'].astype(int)
    df.rename(columns={"MP": "Seconds_Played"}, inplace=True)
    df['Year'] = df['GameID'].str[:4]
    df['Month'] = df['GameID'].str[4:6]
    df['Day'] = df['GameID'].str[6:8]
    return df

def add_odds_columns(df : pd.DataFrame, odds_labels : list[float]):
    """
    Iterates through specified odds and creates variable in NBA statistics CSV for use in prediction

    Parameters:
        df (pd.DataFrame) : dataframe containing raw current NBA season box score statistics
        odds_labels (list) : contains current odds from odds_df that should be calculated
            using specified statistics
    """
    odds_to_columns_map = {
        'rebs+asts': ['TRB', 'AST'],
        'pts+asts': ['PTS', 'AST'],
        'pts+rebs': ['PTS', 'TRB'],
        'pts+rebs+asts': ['PTS', 'TRB', 'AST'],
        'assists': ['AST'],
        'rebounds': ['TRB'],
        'points': ['PTS']
    }
    for columns in odds_to_columns_map.values():
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    for odds_label, columns in odds_to_columns_map.items():
        if odds_label in odds_labels:
            df[odds_label] = df[columns].sum(axis=1)
    return df

def calculate_weighted_avg(previous_games : pd.DataFrame, column : str, weights : list[float]):
    """
    Uses weights that put more importance on recent games and calculate
    a weighted average for specified variable.

    Parameters:
        previous_games (pd.DataFrame) : dataframe of a specific player's game stats
        column (str) : name of variable to calculate weighted average for
        weights (list) : list of weights for the weighted average calculation
    """
    recent_values = previous_games[column].values[-len(weights):]
    recent_values = [float(x) for x in recent_values]
    adjusted_weights = weights[-len(recent_values):]
    return np.average(recent_values, weights=adjusted_weights)

def generate_labels_and_predictions(nba_df : pd.DataFrame, weights : list):
    """
    Uses calculate_weighted_average to calculate artifical points predictions
    which are compared to actual points and used to create binary labels for
    exceeded_expectations.

    Parameters:
        df (pd.DataFrame) : dataframe containing raw current NBA season box score statistics
        weights (list) : list of weights for the weighted average calculation
    """
    nba_df['date'] = pd.to_datetime(nba_df[['Year', 'Month', 'Day']])
    nba_df.sort_values(by=['Player', 'date'], inplace=True)
    predictions = []
    labels = []
    for player in nba_df['Player'].unique():
        player_data = nba_df[nba_df['Player'] == player]
        for i, row in player_data.iterrows():
            previous_games = player_data[player_data['date'] < row['date']]
            if len(previous_games) < len(weights):
                predictions.append(np.nan)
                labels.append(np.nan)
                continue
            weighted_avg = calculate_weighted_avg(previous_games, 'PTS', weights)
            predictions.append(weighted_avg)
            actual_pts = row['PTS']
            label = 1 if float(actual_pts) > weighted_avg else 0
            labels.append(label)
    nba_df['Predicted_PTS'] = predictions
    nba_df['Exceeds_Prediction'] = labels
    return nba_df


def data_clean():
    """
    Function that includes all cleaning functions grouped together
    so users can clean data after refreshing.

    Parameters:
        None
    """
    NBA_df = pd.read_csv(DATA_PATHS['RAW_NBA'])
    NBA_df = column_fixing(NBA_df)
    NBA_df = type_change(NBA_df)
    odds_labels = ['rebs+asts', 'pts+asts', 'pts+rebs', 'pts+rebs+asts', 'assists', 'rebounds', 'points']
    NBA_df = add_odds_columns(NBA_df, odds_labels)
    weights = [0.5, 0.25, 0.15, 0.07, 0.03]
    NBA_df = generate_labels_and_predictions(NBA_df, weights)
    NBA_df.to_csv(DATA_PATHS['PROCESSED_NBA'], index=False)
