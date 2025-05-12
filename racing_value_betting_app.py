import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import date

st.set_page_config(page_title="Horse Racing Value Bets", layout="centered")
st.title("UK Horse Racing Value Betting App")

# --- Select race type ---
race_type = st.sidebar.selectbox("Race Type", ["Flat", "Jumps"]).lower()
today = date.today().isoformat()

# --- API Auth ---
try:
    username = st.secrets["racing_api"]["username"]
    password = st.secrets["racing_api"]["password"]
except KeyError:
    st.error("API credentials not found. Please configure them in Streamlit secrets.")
    st.stop()

# --- API Token ---
@st.cache_data(ttl=3600)
def get_token():
    try:
        r = requests.post(
            "https://theracingapi.com/api/token",
            json={"username": username, "password": password},
            timeout=10
        )
        r.raise_for_status()
        return r.json()["token"]
    except Exception as e:
        st.error("API authentication failed.")
        return None

# --- Fetch race data ---
def fetch_races(race_type):
    token = get_token()
    if not token:
        return None, "Could not authenticate with the racing API."
    
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://theracingapi.com/api/races?date={today}&country=GB&type={race_type}"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.RequestException:
        return None, "API service currently unavailable or timed out."

# --- Fetch odds (mock) ---
def generate_mock_odds(runners):
    odds = {}
    for r in runners:
        odds[r["name"]] = np.round(np.random.uniform(2.5, 21), 2)
    return odds

# --- Calculate value ---
def compute_value_bets(race):
    runners = race["runners"]
    odds = generate_mock_odds(runners)
    total_prob = sum([1 / o for o in odds.values()])
    
    data = []
    for runner in runners:
        name = runner["name"]
        price = odds[name]
        fair_prob = 1 / price
        adjusted_prob = fair_prob / total_prob
        ev = round(price * adjusted_prob - 1, 3)
        ew_ev = round((price / 5 * adjusted_prob) - 0.5, 3)
        data.append({
            "Horse": name,
            "Odds": price,
            "Adj. Prob": round(adjusted_prob, 3),
            "EV": ev,
            "EW EV": ew_ev,
        })
    df = pd.DataFrame(data).sort_values("EV", ascending=False)
    return df

# --- Main Execution ---
st.subheader(f"UK {race_type.capitalize()} Races on {today}")

races_data, error = fetch_races(race_type)
if error:
    st.warning(error)
elif not races_data:
    st.info("No races found for today.")
else:
    for race in races_data[:5]:  # Limit to 5 for API efficiency
        st.markdown(f"### {race['track']} â {race['time']}")
        df = compute_value_bets(race)
        st.dataframe(df, use_container_width=True)
        time.sleep(0.6)  # Rate limit: 2 req/sec max
