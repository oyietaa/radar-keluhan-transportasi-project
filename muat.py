import json
import pandas as pd
import streamlit as st
from config import CLEAN_CSV, RINGKASAN

@st.cache_data(ttl=600)
def muat_data():
    return pd.read_csv(CLEAN_CSV, parse_dates=["at"])

@st.cache_data(ttl=600)
def muat_ringkasan():
    return json.loads(RINGKASAN.read_text(encoding="utf-8"))