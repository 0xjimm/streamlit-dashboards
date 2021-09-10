import streamlit as st
import pandas as pd

# Basic setup and app layout
# st.set_page_config(layout="wide")
st.title("TeFIRE Calculator")

# User inputs on the control panel
st.sidebar.title("Inputs")

# Anchor Earn
ust_deposited = st.sidebar.slider(
    "UST Deposit in Anchor Earn",
    min_value=10,
    max_value=1000,
    value=100,
    step=1,
    format="$%.2f",
    help="What do you think the future price of Luna will be?",
)

# Luna Price
luna_price = st.sidebar.slider(
    "Price of Luna",
    min_value=10,
    max_value=1000,
    value=100,
    step=1,
    format="$%.2f",
    help="What do you think the future price of Luna will be?",
)

# Luna Staked
luna_staked = st.sidebar.slider(
    "Staked Luna",
    min_value=100,
    max_value=20000,
    value=1000,
    step=1,
    help="How much Luna do you plan to stake?",
)

# Staking APR
luna_apr = st.sidebar.slider(
    "Luna Rewards APR",
    min_value=1,
    max_value=50,
    value=10,
    step=1,
    format="%f%%",
    help="What do you think staking rewards will be?",
)

# pLuna and yLuna Ratio
pluna_yluna_ratio = st.sidebar.slider(
    "pLuna to yLuna Ratio",
    min_value=0.0,
    max_value=1.0,
    value=0.85,
    step=0.01,
    help="What do you pLuna will be worth relative to yLuna?",
)

st.header("Anchor Protocol")
st.write("Scenario for monthly cashflow via Anchor Earn.")

st.header("Luna Staking")
st.write("Scenario for monthly cashflow via Staking Luna.")

st.header("Prism Protocol")
st.write("Scenario for decomposing annual Luna staking rewards into pLuna-yLuna.")

staking_rewards = luna_staked * luna_apr / 100
pluna = staking_rewards * pluna_yluna_ratio
yluna = staking_rewards - pluna
purchased_yluna = pluna / (1 - pluna_yluna_ratio)
total_yluna = yluna + purchased_yluna
annual_cash_flow = total_yluna * luna_apr * luna_price / 100

st.write(f"Staking Rewards: {staking_rewards:.2f} Luna")
st.write(f"Decomposed Principal Token: {pluna:.2f} pLuna")
st.write(f"Decomposed Yield Token: {yluna:.2f} yLuna")
st.write(f"Total Yield Token: {total_yluna:.2f} yLuna")
st.write(f"Annual Cashflow: ${annual_cash_flow:,.2f}")
st.write(f"Monthly Cashflow: ${annual_cash_flow/12:,.2f}")
