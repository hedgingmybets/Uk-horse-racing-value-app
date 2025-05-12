import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="UK Horse Racing Value Bets", layout="centered")
st.title("UK Horse Racing — Value Betting Dashboard")

# Load credentials from Streamlit secrets
username = st.secrets["racing_api"]["username"]
password = st.secrets["racing_api"]["password"]

# Authenticate and fetch token
auth_url = "https://theracingapi.com/api/token"
auth_data = {
    "username": username,
    "password": password
}
auth_res = requests.post(auth_url, json=auth_data)
if auth_res.status_code != 200:
    st.error("Authentication failed. Check your credentials.")
    st.stop()

token = auth_res.json().get("token")
headers = {"Authorization": f"Bearer {token}"}

# Fetch today’s UK races
races_url = "https://theracingapi.com/api/racecards"
params = {
    "date": datetime.today().strftime("%Y-%m-%d"),
    "country": "GB",
    "type": "all"
}
response = requests.get(races_url, headers=headers, params=params)

if response.status_code != 200:
    st.error("Failed to fetch race data.")
    st.stop()

races = response.json().get("data", [])
if not races:
    st.info("No UK races available today.")
    st.stop()

# Display available races
for meeting in races:
    st.subheader(meeting["course"])
    for race in meeting.get("races", []):
        st.markdown(f"**Race Time:** {race['time']} — **Race Type:** {race['race_type']}")
        horses = race.get("horses", [])
        data = []
        for h in horses:
            if "odds_decimal" in h and h["odds_decimal"]:
                win_odds = float(h["odds_decimal"])
                implied_prob = round(1 / win_odds, 3)
                value = round((implied_prob * win_odds) - 1, 3)
                data.append({
                    "Horse": h["name"],
                    "Odds": win_odds,
                    "Implied %": f"{implied_prob*100:.1f}%",
                    "Value": value
                })
        if data:
            df = pd.DataFrame(data)
            df = df.sort_values(by="Value", ascending=False)
            st.dataframe(df)
        st.markdown("---")