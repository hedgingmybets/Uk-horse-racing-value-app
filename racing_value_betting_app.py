import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import date

st.set_page_config(page_title="Horse Racing Value Bets", layout="centered")
st.title("Horse Racing Value Betting App — OddsAPI + SportsDB")

today = date.today().isoformat()
country = "GB"

# --- API Keys from Streamlit secrets ---
try:
    odds_api_key = st.secrets["theoddsapi"]["api_key"]
    sportsdb_key = st.secrets["thesportsdb"]["api_key"]
except KeyError:
    st.error("API keys not configured. Add them via Streamlit secrets.")
    st.stop()

# --- Fetch races from SportsDB (mocked UK race list) ---
@st.cache_data(ttl=3600)
def fetch_races():
    url = f"https://www.thesportsdb.com/api/v1/json/{sportsdb_key}/eventsday.php?d={today}&s=Horse_Racing"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json().get("events", [])
        races = [{"track": e["strEvent"], "time": e["dateEvent"]} for e in data if e.get("strCountry") == country]
        return races
    except Exception:
        return []

# --- Fetch odds from TheOddsAPI ---
@st.cache_data(ttl=600)
def fetch_odds():
    url = "https://api.the-odds-api.com/v4/sports/horse_racing/odds"
    params = {
        "apiKey": odds_api_key,
        "regions": "uk",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

# --- Compute EV (example logic) ---
def compute_value_bets(track_name, odds_data):
    runners = ["Runner A", "Runner B", "Runner C"]
    prices = np.random.uniform(2.0, 15.0, size=len(runners))
    probs = 1 / prices
    adjusted_probs = probs / sum(probs)
    data = []
    for i, runner in enumerate(runners):
        ev = round(prices[i] * adjusted_probs[i] - 1, 3)
        ew_ev = round((prices[i] / 5 * adjusted_probs[i]) - 0.5, 3)
        data.append({
            "Horse": runner,
            "Odds": round(prices[i], 2),
            "Adj. Prob": round(adjusted_probs[i], 3),
            "EV": ev,
            "EW EV": ew_ev
        })
    return pd.DataFrame(data).sort_values("EV", ascending=False)

# --- Main Execution ---
races = fetch_races()
odds = fetch_odds()

if not races:
    st.warning("No races found for today.")
else:
    for race in races[:5]:
        st.markdown(f"### {race['track']} — {race['time']}")
        df = compute_value_bets(race["track"], odds)
        st.dataframe(df, use_container_width=True)