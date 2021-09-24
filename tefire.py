import streamlit as st
import pandas as pd
from PIL import Image

# Basic setup and app layout
# st.set_page_config(layout="wide")
st.title("TeFIRE Calculator")

# User inputs on the control panel
st.sidebar.title("Inputs")

# Anchor Earn
ust_deposited = st.sidebar.number_input(
    "Anchor Earn Deposit in UST",
    min_value=1000,
    max_value=10_000_000_000,
    value=1_000_000,
    step=1000,
    format="%.2d",
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
    max_value=50_000,
    value=10_000,
    step=100,
    help="How much Luna do you plan to stake?",
)

# Staking APR
luna_apr = st.sidebar.slider(
    "Staking Return",
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
    max_value=0.99,
    value=0.90,
    step=0.01,
    help="What do you pLuna will be worth relative to yLuna?",
)

st.markdown(
    """
    Recently, I conducted a poll on [Twitter](https://twitter.com/lejimmy/status/1435017886226124803?s=20) asking the community about "making it" in crypto and what that might translate to in terms of monthly income.
    
    In this thread, I explored a few ways that you could generate this monthly income in the Terra Luna ecosystem.

    Of course, there were many assumptions made.  With this tool, you can play around with your projections and consider your financial goals on your journey to "making it."

    """
)

st.write(
    "If you found this useful and would like to support more of this type of work, consider contributing to my wallet here: *terra1m3sl9qea92km6mqm02yqxfygn8g9acl8wzj6x7*"
)

st.error(
    "Disclaimer: This tool was created by a smooth brain.  Do not consider such information as investment advice."
)

st.markdown("## **Anchor Protocol**")

annual_interest = ust_deposited * earn_apy / 100
monthly_interest = annual_interest / 12

st.markdown(
    f"""
    Depositing UST into Anchor Earn is the simplest path to a stable income.

    A **${ust_deposited:,.2f} UST deposit**, at **{earn_apy}% APY** will earn an estimated **${annual_interest:,.2f} per year** or roughly **${monthly_interest:,.2f} per month**.
    
    If you are withdrawing your monthly income every month, you would expect a little less as the funds are not compounding for the entire year.  To be extremely precise, you would want to calculate the USD gained per block and only compound for the periods between withdrawal.
    """
)

st.markdown("## **Staking Luna**")
staking_rewards = luna_staked * luna_apr / 100
staking_rewards_usd = staking_rewards * luna_price
monthly_usd = staking_rewards_usd / 12

st.markdown(
    f"""
    By staking or delegating your Luna to a validator, you earn staking rewards paid in Luna, Terra stablecoins, and protocol airdrops.

    Staking rewards are projected to increase to double digit APRs after the Col-5 mainnet upgrade.

    At a **{luna_apr}% APR** staking return, **{luna_staked:,} Luna** staked, valued at **${luna_staked*luna_price:,.2f}**, will earn an equivalent of **{staking_rewards:,.2f} Luna** per year.

    If you sold all of the staking rewards at **${luna_price} per Luna**, you would earn a total of **${staking_rewards_usd:,.2f} per year** or roughly **${staking_rewards_usd/12:,.2f} per month**.
     """
)


st.markdown("## **Prism Protocol**")
total_yluna = staking_rewards / (1 - pluna_yluna_ratio)
annual_yluna_rewards_usd = total_yluna * luna_price * luna_apr / 100

st.markdown(
    f"""
    With Prism, you can decompose your **staking rewards of {staking_rewards:,.2f} Luna** into a principal and yield component.  This allows you to speculate only on the price of Luna or only on the cash flow that your Luna may generate.

    If the market values these components at a **{pluna_yluna_ratio} pLuna to yLuna ratio**, pLuna tokens can be swapped for a total of **{total_yluna:,.2f} yLuna** tokens.

    Over the next year, the yLuna will generate **${annual_yluna_rewards_usd:,.2f}** in rewards or roughly **${annual_yluna_rewards_usd/12:,.2f} per month.**

    
    """
)

prism_staking_diff = annual_yluna_rewards_usd / 12 - staking_rewards_usd / 12

if prism_staking_diff > 0:
    st.markdown(
        f"In this scenario, you would make **${prism_staking_diff:,.2f} more per month** by decomposing and swapping into yLuna versus selling your staking rewards outright."
    )
elif prism_staking_diff < 0:
    st.markdown(
        f"In this scenario, you would make **${abs(prism_staking_diff):,.2f} less per month** by decomposing and swapping into yLuna versus selling your staking rewards outright."
    )
else:
    st.markdown(
        "In this scenario, selling your staking rewards and swapping to yLuna would yield the same in terms of monthly income."
    )

st.markdown(
    """
    Of course this gets to become complicated and nuanced very quickly when you introduce the 3, 6, 9, and 12 month expiration dates of these components.

    The yLuna expiry dates may overlap and the market may value them at varying rates.  You could potentially swap yLuna expiring in Dec 2022 half way through the term with a newly yLuna contract expiring in Dec 2023. 

    """
)

st.markdown("### **Closing Thoughts**")
st.markdown(
    f"""
    I hope this was useful, perhaps a bit insightful, and as always, wagmi.

    Feel free to reach out to me on Twitter [@lejimmy](https://twitter.com/lejimmy) if you have any questions or feedback.
     
    If you're inclined to contribute directly, please fork the [Github Repo here](https://github.com/lejimmy/streamlit-dashboards).

    """
)
