import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

st.set_page_config(page_title="Horse Racing Value Betting", layout="wide")
st.title("UK Horse Racing Value Betting (Prototype)")

st.markdown("This prototype estimates value in UK races using simulated probabilities and bookmaker odds.")

# Simulate some upcoming races
races = [
    {"race": "Kempton 14:30", "runner": "Speed Flyer", "odds": 3.5, "win_prob": 0.32, "place_prob": 0.65},
    {"race": "Kempton 14:30", "runner": "Bold Spirit", "odds": 5.0, "win_prob": 0.20, "place_prob": 0.45},
    {"race": "Kempton 14:30", "runner": "Golden Arrow", "odds": 7.0, "win_prob": 0.14, "place_prob": 0.35},
    {"race": "Chepstow 15:10", "runner": "Misty River", "odds": 4.0, "win_prob": 0.28, "place_prob": 0.6},
    {"race": "Chepstow 15:10", "runner": "Ocean Gale", "odds": 6.5, "win_prob": 0.18, "place_prob": 0.42},
    {"race": "Chepstow 15:10", "runner": "Captain Jack", "odds": 8.0, "win_prob": 0.12, "place_prob": 0.3}
]

df = pd.DataFrame(races)
df["EV Win"] = (df["win_prob"] * df["odds"]) - 1
df["EV Place"] = (df["place_prob"] * (df["odds"] / 3)) - 1
df["Best Bet Type"] = np.where(df["EV Win"] > df["EV Place"], "Win", "Place")
df["Best EV"] = df[["EV Win", "EV Place"]].max(axis=1)

race_selected = st.selectbox("Select a Race", df["race"].unique())
filtered = df[df["race"] == race_selected]

st.write(f"### Runners in {race_selected}")
st.dataframe(filtered[["runner", "odds", "win_prob", "place_prob", "EV Win", "EV Place", "Best Bet Type", "Best EV"]])
