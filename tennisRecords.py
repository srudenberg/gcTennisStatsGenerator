import requests
from bs4 import BeautifulSoup
import csv
import os
import csv
import pandas as pd

# Suppress SSL certificate verification warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

year = input("Enter Year: ")

url = 'https://grinnell_ftp.sidearmsports.com/custompages/mten/' + year + '/teamigbg.htm'

# Fetch the HTML content from the URL, bypassing SSL certificate verification
response = requests.get(url, verify=False)
html_content = response.text

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <td> tags with a <font> tag inside
td_tags = soup.find_all('td')

# Extract the information inside the <font> tag within each <td> tag
data = []
player_name = None
for td_tag in td_tags:
    # Check if <b> tag is found within <td> tag
    b_tag = td_tag.find('b')
    if b_tag:
        # Extract player name
        player_name = b_tag.get_text().strip('" \n')
    font_tag = td_tag.find('font')
    if font_tag:
        # Append player name and information inside <font> tag
        if player_name:
            data.append([player_name, font_tag.get_text().strip()])

# Get the path to the user's directory
directory = os.path.expanduser('~')

# Construct the full file path
csv_file = os.path.join(directory, 'tennis_data_' + year + '.csv')

with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write header
    writer.writerow(['Player Name', 'Information'])
    # Write data
    writer.writerows(data)

#print(f"Data has been written to {csv_file}")

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file)

# List of strings to replace with an empty string
strings_to_replace = ['Nat/Reg', 'Ranking', 'Team/School', 'Pos', 
                      'Opponent (Rank)', 'Opponent (Rank )', 'Schedule legend',
                      'SINGLES', 'Singles score', 'DOUBLES', 'Doubles score']

# Replace specified strings with an empty string in the 'Player Name' column
for string in strings_to_replace:
    df['Player Name'] = df['Player Name'].str.replace(string, '')

# Strip spaces from 'Player Name' and 'Information' columns
df['Player Name'] = df['Player Name'].str.strip()
df['Information'] = df['Information'].str.strip()

# Drop rows containing NaN in any column except 'Player Name'
df.dropna(subset=df.columns.difference(['Player Name']), inplace=True)

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Check if the 'Player Name' equals the 'Information' value
    if row['Player Name'] != row['Information']:
        # Check if the 'Information' value contains 'Won' or 'Lost'
        if 'Won' not in row['Information'] and 'Lost' not in row['Information']:
            # If it doesn't contain 'Won' or 'Lost', drop the row from the DataFrame
            df.drop(index, inplace=True)

# Reset the index after dropping rows
df.reset_index(drop=True, inplace=True)

#print(df)

# Sorting into a Class 

# Define the Player class
class Player:
    def __init__(self, name, singles_wins=0, singles_losses=0, doubles_wins=0, doubles_losses=0):
        self.name = name
        self.singles_wins = singles_wins
        self.singles_losses = singles_losses
        self.doubles_wins = doubles_wins
        self.doubles_losses = doubles_losses

    def calculate_stats(self):
        self.singles_total = self.singles_wins + self.singles_losses
        self.doubles_total = self.doubles_wins + self.doubles_losses
        
        if self.singles_total > 0:
            self.singles_perc = self.singles_wins / self.singles_total
        else:
            self.singles_perc = 0
        
        if self.doubles_total > 0:
            self.doubles_perc = self.doubles_wins / self.doubles_total
        else:
            self.doubles_perc = 0
        
        self.total_wins = self.singles_wins + self.doubles_wins
        self.total_losses = self.singles_losses + self.doubles_losses

# List to store player objects
players = []

# Initialize variables to track wins and losses
current_player_name = None
singles_wins = 0
singles_losses = 0
doubles_wins = 0
doubles_losses = 0

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    # Check if the 'Player Name' equals the 'Information' value
    if row['Player Name'] == row['Information']:
        # Save the current player's stats before moving to the next player
        if current_player_name is not None:
            player = Player(current_player_name, singles_wins, singles_losses, doubles_wins, doubles_losses)
            players.append(player)
        
        # Update current player name and reset win/loss counters
        current_player_name = row['Player Name']
        singles_wins = 0
        singles_losses = 0
        doubles_wins = 0
        doubles_losses = 0
    else:
        # Check if the match is singles or doubles
        if '/' in str(row['Information']):
            if 'Won' in row['Information']:
                doubles_wins += 1
            elif 'Lost' in row['Information']:
                doubles_losses += 1
        else:
            if 'Won' in row['Information']:
                singles_wins += 1
            elif 'Lost' in row['Information']:
                singles_losses += 1

# Add the last player's stats
if current_player_name is not None:
    player = Player(current_player_name, singles_wins, singles_losses, doubles_wins, doubles_losses)
    players.append(player)

# Calculating stats for each player
for player in players:
    player.calculate_stats()

# Collect player statistics into a list of dictionaries
player_stats = []
for player in players:
    player_stats.append({
        'Player Name': player.name,
        'Singles Wins': player.singles_wins,
        'Singles Losses': player.singles_losses,
        'Singles Percentage': player.singles_perc,
        'Doubles Wins': player.doubles_wins,
        'Doubles Losses': player.doubles_losses,
        'Doubles Percentage': player.doubles_perc,
        'Total Wins': player.total_wins,
        'Total Losses': player.total_losses,
        'Total Matches': player.singles_total + player.doubles_total,
        'Overall Win Percentage': player.total_wins / (player.singles_total + player.doubles_total) if (player.singles_total + player.doubles_total) > 0 else 0
    })

# Create a DataFrame from the list of dictionaries
df_players = pd.DataFrame(player_stats)

# Finding players with the highest stats
most_singles_wins_player = df_players.loc[df_players['Singles Wins'].idxmax()]
highest_singles_perc_player = df_players.loc[df_players['Singles Percentage'].idxmax()]
most_doubles_wins_player = df_players.loc[df_players['Doubles Wins'].idxmax()]
highest_doubles_perc_player = df_players.loc[df_players['Doubles Percentage'].idxmax()]
most_total_wins_player = df_players.loc[df_players['Total Wins'].idxmax()]

# Create a new column "Best" and initialize it with empty lists
df_players['Best'] = ''

# Populate the "Best" column with corresponding text for each player
df_players.loc[df_players['Player Name'] == most_singles_wins_player['Player Name'], 'Best'] += 'most singles wins, '
df_players.loc[df_players['Player Name'] == highest_singles_perc_player['Player Name'], 'Best'] += 'highest singles percentage, '
df_players.loc[df_players['Player Name'] == most_doubles_wins_player['Player Name'], 'Best'] += 'most doubles wins, '
df_players.loc[df_players['Player Name'] == highest_doubles_perc_player['Player Name'], 'Best'] += 'highest doubles percentage, '
df_players.loc[df_players['Player Name'] == most_total_wins_player['Player Name'], 'Best'] += 'most total wins, '

# Remove the trailing comma and space from the end of the text
df_players['Best'] = df_players['Best'].str.rstrip(', ')

# Print the DataFrame with the new "Best" column
# print(df_players)

# Get the path to the user's directory
directory = os.path.expanduser('~')

# Construct the full file path
csv_file_path = os.path.join(directory, 'player_stats_' + year + '.csv')

# Export the DataFrame to the CSV file
df_players.to_csv(csv_file_path, index=False)

# Print the path where the file is exported
print("CSV exported to:", csv_file_path)
