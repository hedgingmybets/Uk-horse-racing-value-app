import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import numpy as np

st.set_page_config(page_title="UK Horse Racing Value Bets", layout="wide")
st.title("UK Horse Racing Value Betting Dashboard with Each-Way")

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

race_type = st.sidebar.radio("Race Type", ["flat", "jumps"])
st.subheader(f"Fetching today's UK {race_type} races...")

try:
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    if response.status_code == 200:
        races = response.json()
        if races:
            st.success(f"Found {len(races)} races.")
            race_df = pd.DataFrame(races)

            all_bets = []
            for _, race in race_df.iterrows():
                race_id = race.get("id")
                # Simulated horses for now â replace with actual runners endpoint
                num_runners = np.random.randint(5, 12)
                horses = [f"Horse {i+1}" for i in range(num_runners)]
                probs = np.random.dirichlet(np.ones(num_runners)).flatten()
                win_odds = [round(1/p, 2) for p in probs]
                bookmaker_odds = [round(o * np.random.uniform(0.9, 1.1), 2) for o in win_odds]
                ev_win = [round((p * b) - 1, 2) for p, b in zip(probs, bookmaker_odds)]

                # Each-way: 1/5 odds for place, top 3 finishers (if >7 runners)
                ew_fraction = 1/5
                places = 3 if num_runners > 7 else 2 if num_runners >= 5 else 1
                ew_odds = [round(o * ew_fraction, 2) for o in bookmaker_odds]
                ew_prob = [sum(sorted(probs, reverse=True)[:places]) / num_runners for _ in horses]
                ev_ew = [round((ep * eo) - 1, 2) for ep, eo in zip(ew_prob, ew_odds)]

                df = pd.DataFrame({
                    "Race": race["title"],
                    "Horse": horses,
                    "Win Prob": probs,
                    "Book Win Odds": bookmaker_odds,
                    "Win EV": ev_win,
                    "Place Prob": ew_prob,
                    "EW Odds": ew_odds,
                    "Place EV": ev_ew
                })
                value_df = df[(df["Win EV"] > 0) | (df["Place EV"] > 0)]
                if not value_df.empty:
                    all_bets.append(value_df)

            if all_bets:
                st.write("**Horses with positive EV (Win or Each-Way):**")
                st.dataframe(pd.concat(all_bets, ignore_index=True))
            else:
                st.info("No value opportunities found today.")
        else:
            st.info("No races found.")
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
except requests.exceptions.RequestException as e:
    st.error(f"API error: {e}")