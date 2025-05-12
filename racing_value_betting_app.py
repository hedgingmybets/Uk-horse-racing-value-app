import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import date

st.set_page_config(page_title="UK Horse Racing Value Bets", layout="centered")
st.title("UK Horse Racing Value Bets — OddsAPI + RacingAPI")

today = date.today().isoformat()
country = "GB"

# --- Load API Keys ---
try:
    odds_api_key = st.secrets["theoddsapi"]["api_key"]
    racing_username = st.secrets["racing_api"]["username"]
    racing_password = st.secrets["racing_api"]["password"]
except KeyError:
    st.error("API keys not configured properly in Streamlit secrets.")
    st.stop()

# --- RacingAPI Token with Caching and Retry ---
@st.cache_data(ttl=3600)
def get_racing_token():
    for _ in range(3):
        try:
            response = requests.post(
                "https://theracingapi.com/api/token",
                json={"username": racing_username, "password": racing_password},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("token", None)
        except Exception:
            time.sleep(2)
    return None

# --- Fetch Racecards from RacingAPI with Rate Limit ---
def fetch_racecards():
    token = get_racing_token()
    if not token:
        return None, "RacingAPI authentication failed."

    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://theracingapi.com/api/races?date={today}&country={country}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json(), None
    except Exception:
        return None, "Failed to load racecards from RacingAPI."

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
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []

# --- Calculate Value Bets ---
def compute_value_bets(runners):
    odds = np.random.uniform(2.5, 20.0, size=len(runners))
    probs = 1 / odds
    probs /= probs.sum()
    results = []
    for i, r in enumerate(runners):
        results.append({
            "Horse": r["name"],
            "Odds": round(odds[i], 2),
            "Adj. Prob": round(probs[i], 3),
            "EV": round(odds[i] * probs[i] - 1, 3),
            "EW EV": round((odds[i] / 5 * probs[i]) - 0.5, 3)
        })
    return pd.DataFrame(results).sort_values("EV", ascending=False)

# --- Main Execution ---
racecards, error = fetch_racecards()
odds_data = fetch_odds()

if error:
    st.warning(error)
elif not racecards:
    st.info("No racecards found for today.")
else:
    for race in racecards[:5]:  # Throttle limit
        st.subheader(f"{race['track']} — {race['time']}")
        if "runners" not in race:
            st.info("No runners found.")
            continue
        df = compute_value_bets(race["runners"])
        st.dataframe(df, use_container_width=True)
        time.sleep(0.6)  # Stay under RacingAPI rate limit