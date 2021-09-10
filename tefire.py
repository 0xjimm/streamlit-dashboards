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
    max_value=10000000,
    value=10000,
    step=100,
    format="$%.2f",
    help="What do you think the future price of Luna will be?",
)

# Anchor Earn APY
earn_apy = st.sidebar.slider(
    "Anchor Earn APY",
    min_value=0.0,
    max_value=40.0,
    value=19.5,
    step=0.01,
    help="What do you think future Anchor Earn APY will be?",
)

# Luna Price
luna_price = st.sidebar.slider(
    "Price of Luna",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    format="$%.2f",
    help="What do you think the future price of Luna will be?",
)

# Luna Staked
luna_staked = st.sidebar.slider(
    "Staked Luna",
    min_value=100,
    max_value=20000,
    value=1000,
    step=100,
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
fv = ust_deposited * earn_apy / 100 + ust_deposited
fv_ust_deposited = fv / ust_deposited
int_periods = fv_ust_deposited / 5256000
epoch_interest = pow(fv_ust_deposited, int_periods) - 1
usd_day = ust_deposited * epoch_interest * 14400
usd_month = ust_deposited * epoch_interest * 438000
st.write(f"Interest earned per day: ${usd_day:,.2f}.")
st.write(f"Interest earned per month: ${usd_month:,.2f}.")


st.header("Luna Staking")
st.write("Scenario for monthly cashflow via Staking Luna.")
staking_rewards = luna_staked * luna_apr / 100
staking_rewards_usd = staking_rewards * luna_price
monthly_usd = staking_rewards_usd / 12
st.write(f"Staking Rewards: {staking_rewards:.2f} Luna")
st.write(f"Staking Rewards in USD: ${staking_rewards_usd:,.2f}")
st.write(f"Monthly Rewards in USD: ${monthly_usd:,.2f}")


st.header("Prism Protocol")
st.write("Scenario for decomposing annual Luna staking rewards into pLuna-yLuna.")
total_yluna = staking_rewards / (1 - pluna_yluna_ratio)
annual_cash_flow = total_yluna * luna_price

st.write(f"Staking Rewards: {staking_rewards:.2f} Luna")
st.write(f"Decomposed Principal Tokens to Sell: {staking_rewards:.2f} pLuna")
st.write(f"Decomposed Yield Tokens: {staking_rewards:.2f} yLuna")
st.write(f"Total Yield Tokens: {total_yluna:.2f} yLuna")
st.write(f"Annual Cashflow: ${annual_cash_flow:,.2f}")
st.write(f"Monthly Cashflow: ${annual_cash_flow/12:,.2f}")
