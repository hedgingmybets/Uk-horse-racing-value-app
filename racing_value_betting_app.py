import streamlit as st
import requests

st.set_page_config(page_title="API Debugger", layout="centered")
st.title("Racing API Authentication Debug Tool")

# Inputs
username = st.text_input("API Username")
password = st.text_input("API Password", type="password")

if st.button("Test Authentication"):
    try:
        with st.spinner("Sending request..."):
            response = requests.post(
                "https://theracingapi.com/api/token",
                json={"username": username, "password": password},
                timeout=15
            )
        st.write("Status Code:", response.status_code)
        st.write("Response Headers:", dict(response.headers))
        try:
            st.json(response.json())
        except Exception:
            st.write("Raw Response Text:", response.text)
    except Exception as e:
        st.error(f"Exception occurred: {e}")