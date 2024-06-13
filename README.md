# gcTennisStatsGenerator (Webscraper) 

This Python script fetches tennis player statistics from a specific URL, processes the data using pandas, and creates multiple summary statistics for each player's season record. 

## Setup Instructions

1. **Clone the repository:**

        git clone https://github.com/srudenberg/gcTennisStatsGenerator.git

        cd gcTennisStatsGenerator

3. **Install dependencies:**

Make sure you have Python 3.11.5 installed. 

    python --version

Then, install required Python packages using pip:

    pip install -r requirements.txt

3. **Run the script:**

Run the main script and follow the prompts:

    python tennisRecords.py

## Usage

- User will be prompted to enter a year. 
- The code will scrape records and create statistics for:
-   Singles Wins/Losses/Percentage, Doubles Wins/Losses/Percentage, Total Wins/Losses/Matches, Overall Win Percentage, and a "Best" Category. 
- These statistics will be outputted in a CSV file to your home directory. 
