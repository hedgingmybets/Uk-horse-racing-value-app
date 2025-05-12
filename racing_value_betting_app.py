import streamlit as st
import pandas as pd
import requests
from datetime import date

st.set_page_config(page_title="UK Horse Racing Value Bets", layout="wide")
st.title("UK Horse Racing Value Betting Dashboard")

# Retrieve credentials securely from secrets
username = st.secrets["racing_api"]["username"]
password = st.secrets["racing_api"]["password"]
auth = (username, password)

# Input: Select race type
race_type = st.sidebar.selectbox("Race Type", ["flat", "jumps"])
race_date = st.sidebar.date_input("Race Date", date.today())

# Fetch race data
@st.cache_data(ttl=600)
def fetch_race_data(race_type, race_date):
    base_url = "https://theracingapi.com/api/races"
    params = {"date": race_date.strftime("%Y-%m-%d"), "country": "GB", "type": race_type}
    try:
        response = requests.get(base_url, auth=auth, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return []

races = fetch_race_data(race_type, race_date)

if not races:
    st.warning("No race data available.")
else:
    for race in races:
        st.subheader(f"{race['course_name']} - {race['race_time']} ({race_type.title()})")
        if 'runners' not in race or not race['runners']:
            st.write("No runner data available.")
            continue

        race_data = []
        for runner in race["runners"]:
            name = runner.get("name", "N/A")
            odds = float(runner.get("odds_decimal", 0))
            win_prob = round(1 / odds, 3) if odds > 0 else 0
            ev = round((win_prob * odds) - 1, 3)
            race_data.append({"Horse": name, "Odds": odds, "Win Probability": win_prob, "Expected Value": ev})

        df = pd.DataFrame(race_data)
        df = df.sort_values(by="Expected Value", ascending=False).reset_index(drop=True)
        st.dataframe(df)