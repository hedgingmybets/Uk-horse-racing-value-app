import streamlit as st
import requests
import time
import pandas as pd
from datetime import date

st.set_page_config(page_title="Horse Racing Value Betting", layout="wide")
st.title("UK Horse Racing — Value Betting App")

API_KEY = st.secrets["racing_api_key"]
BASE_URL = "https://theracingapi.com/api"

def rate_limited_request(url, headers=None, params=None, delay=0.6):
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        time.sleep(delay)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
        return None

# Select race type and date
race_type = st.sidebar.selectbox("Race Type", ["flat", "jumps"])
race_date = st.sidebar.date_input("Race Date", value=date.today())

# Fetch races
params = {"date": race_date.strftime("%Y-%m-%d"), "country": "GB", "type": race_type}
headers = {"Authorization": f"Bearer {API_KEY}"}
data = rate_limited_request(f"{BASE_URL}/races", headers=headers, params=params)

if data and "races" in data:
    for race in data["races"]:
        st.subheader(f"{race['racecourse']} — {race['time']} — {race['name']}")
        
        # Fetch runners for the race
        race_id = race["id"]
        runners = rate_limited_request(f"{BASE_URL}/races/{race_id}/runners", headers=headers)
        
        if runners and "runners" in runners:
            df = pd.DataFrame(runners["runners"])
            if not df.empty:
                df["Each Way Terms"] = "1/5 3 places"  # Placeholder logic
                df["Bookmaker Odds"] = df.get("odds", 5.0)  # Placeholder odds
                df["Model Win Prob"] = 1 / df["Bookmaker Odds"]
                df["Value Bet"] = (df["Model Win Prob"] * df["Bookmaker Odds"]) > 1.05
                st.dataframe(df[["name", "Bookmaker Odds", "Model Win Prob", "Each Way Terms", "Value Bet"]])
            else:
                st.write("No runner data available.")
        else:
            st.write("No runners found.")
else:
    st.warning("No race data found or API request failed.")