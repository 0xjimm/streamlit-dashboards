import streamlit as st
import plotly.express as px
import pandas as pd
import json

# Basic setup and app layout
st.set_page_config(layout="wide")
st.title("Spaceloot Knowhere Transfers")

st.warning(
    "If you found this useful and would like to support more of this type of work, consider contributing to my wallet here: *terra1m3sl9qea92km6mqm02yqxfygn8g9acl8wzj6x7*"
)

# load tax query into pandas
query_id = "7a881171-55a9-4d67-a170-355c7b6a5728"
df = pd.read_json(
    f"https://api.flipsidecrypto.com/api/v2/queries/{query_id}/data/latest",
    convert_dates=["BLOCK_TIMESTAMP"],
)

# pivot table
df_pivot = df.pivot(
    index="TX_ID", columns="EVENT_TYPE", values=["EVENT_ATTRIBUTES", "BLOCK_TIMESTAMP"]
)

# reindex
df_pivot.columns = ["_".join(tup) for tup in df_pivot.columns.values]

# find messages with 'settle'
df_pivot = df_pivot[
    df_pivot["EVENT_ATTRIBUTES_from_contract"].fillna("").str.contains("settle")
]

# reset index
df_pivot.reset_index(inplace=True)

# extract columns of interest
df_pivot = df_pivot[
    [
        "TX_ID",
        "EVENT_ATTRIBUTES_from_contract",
        "EVENT_ATTRIBUTES_transfer",
        "BLOCK_TIMESTAMP_execute_contract",
    ]
]

# parse raw msg value
df_merge = pd.concat(
    [
        df_pivot,
        pd.json_normalize(df_pivot["EVENT_ATTRIBUTES_from_contract"].apply(json.loads)),
    ],
    axis=1,
)

# parse raw event attributes
df_merge = pd.concat(
    [
        df_merge,
        pd.json_normalize(df_merge["EVENT_ATTRIBUTES_transfer"].apply(json.loads)),
    ],
    axis=1,
)

# parse uluna amount
df_merge["amount"] = df_merge["amount"].explode()

# parse amount dict
df_merge["amount"] = pd.json_normalize(df_merge["amount"])["amount"]

# convert to luna
df_merge["amount"] = df_merge["amount"] / 1_000_000

# drop duplicate sender column
df_merge = df_merge.iloc[:, :-1]

# drop duplicate contract sender columns
df_merge.drop(columns="sender", axis=1, inplace=True)

# rename columns
df_merge.rename(columns={"recipient": "sender"}, inplace=True)
df_merge.columns = [*df_merge.columns[:-1], "recipient"]

# extract columns of itnerest
df_merge = df_merge[
    [
        "TX_ID",
        "BLOCK_TIMESTAMP_execute_contract",
        "sender",
        "recipient",
        "token_id",
        "amount",
    ]
]

# rename columns
df_merge.rename(
    columns={"TX_ID": "tx_id", "BLOCK_TIMESTAMP_execute_contract": "timestamp"},
    inplace=True,
)

# combine with rarity guide
df_rarity = pd.read_csv("SpaceLoot Rarity Guide w_ Colors - rarity.csv")
df_rarity = df_rarity[["Token ID", "Bullish Bear Rating"]]

# merge with rarity guide
df_merge = df_merge.merge(df_rarity, left_on="token_id", right_on="Token ID")
df_merge.drop("Token ID", axis=1, inplace=True)
df_merge.rename(columns={"Bullish Bear Rating": "rarity"}, inplace=True)

# reorder columns
df_merge = df_merge[
    ["tx_id", "timestamp", "sender", "recipient", "token_id", "rarity", "amount"]
]

st.header("Sales Over Time")
st.write(
    "Completed sales over time with rarity as color.  Smaller scores are more rare."
)
fig = px.scatter(
    df_merge,
    x="timestamp",
    y="amount",
    color="rarity",
    color_continuous_scale="Viridis_r",
)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

col1.header("Distribution of Sales")
col1.write("Histogram of auction settlements.")
fig = px.histogram(df_merge, x="amount", nbins=20)
col1.plotly_chart(fig, use_container_width=True)

col2.header("Sales Price vs. Rarity")
col2.markdown(
    "Spaceloot Rarity plotted against [Bullish Bear](https://twitter.com/L_BullishBear)'s Rarity Database.  Smaller scores are more rare."
)
fig = px.scatter(
    df_merge,
    x="rarity",
    y="amount",
)
col2.plotly_chart(fig, use_container_width=True)

st.header("Transactions Table")
st.write("History of completed auction transfers.")
st.write(df_merge)

st.markdown("## **Closing Thoughts**")
st.markdown(
    f"""
    I hope this was useful, perhaps a bit insightful, and as always, wagmi.

    Feel free to reach out to me on Twitter [@lejimmy](https://twitter.com/lejimmy) if you have any questions or feedback.
     
    If you're inclined to contribute directly, please fork the [Github Repo here](https://github.com/lejimmy/streamlit-dashboards).

    """
)
