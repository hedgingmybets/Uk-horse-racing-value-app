import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import numpy as np

st.set_page_config(page_title="UK Horse Racing Value Bets", layout="wide")
st.title("UK Horse Racing Value Betting Dashboard with Each-Way")

# Race type selector (must come before using race_type)
race_type = st.sidebar.radio("Race Type", ["flat", "jumps"])
st.subheader(f"Fetching today’s UK {race_type} races...")

# API token (stored securely via Streamlit secrets)
TOKEN = st.secrets.get("racing_api_token", "YOUR_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Base API URL
url = "https://theracingapi.com/api/races"
params = {
    "date": datetime.today().strftime("%Y-%m-%d"),
    "country": "GB",
    "type": race_type
}

try:
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    if response.status_code == 200:
        races = response.json()
        if races:
            st.success(f"Found {len(races)} races.")
            race_df = pd.DataFrame(races)

            all_bets = []
            for _, row in race_df.iterrows():
                st.markdown(f"### {row['race_time']} — {row['track']} ({row['distance']}m)")

                runners = row.get("runners", [])
                if not runners:
                    st.write("No runner data available.")
                    continue

                table = []
                for runner in runners:
                    win_prob = runner.get("win_probability", 0)
                    ew_prob = runner.get("place_probability", 0)
                    win_odds = runner.get("win_odds", 0)
                    ew_odds = runner.get("place_odds", 0)

                    ev_win = round((win_prob * win_odds) - 1, 2)
                    ev_ew = round((ew_prob * ew_odds) - 1, 2)

                    best = "Win" if ev_win > ev_ew else "E/W"
                    if max(ev_win, ev_ew) < 0:
                        best = "No value"

                    table.append({
                        "Horse": runner["horse"],
                        "Win Odds": win_odds,
                        "E/W Odds": ew_odds,
                        "Win EV": ev_win,
                        "E/W EV": ev_ew,
                        "Best Bet": best
                    })

                df = pd.DataFrame(table)
                st.dataframe(df)
        else:
            st.warning("No races found for today.")
    else:
        st.error(f"Failed to fetch data. Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    st.error(f"Request failed: {e}")