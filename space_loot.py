import streamlit as st
import plotly.express as px
import pandas as pd

# Basic setup and app layout
st.set_page_config(layout="wide")
st.title("Spaceloot Dashboard")

transactions_hash = "0e1550c8-3724-4d93-84e5-76b68b3956d4"
claim_hash = "9485d2f6-010b-4b06-952e-8dcfc265da53"

# load claims into df
df_claim = pd.read_json(
    f"https://api.flipsidecrypto.com/api/v2/queries/{claim_hash}/data/latest",
    convert_dates=["BLOCK_TIMESTAMP"],
)
df_claim = (
    df_claim[["SENDER", "TX_STATUS"]]
    .groupby("SENDER", as_index=False)
    .count()
    .reset_index(drop=True)
    .sort_values(by="TX_STATUS", ascending=False)
)
df_claim.rename(columns={"SENDER": "HOLDER", "TX_STATUS": "CLAIMED"}, inplace=True)

# load transactions into df
df_tx = pd.read_json(
    f"https://api.flipsidecrypto.com/api/v2/queries/{transactions_hash}/data/latest",
    convert_dates=["BLOCK_TIMESTAMP"],
)

# group by hours
df_tx.set_index("BLOCK_TIMESTAMP", inplace=True)
df_grouped = (
    df_tx["TX_STATUS"].groupby(pd.Grouper(freq="H")).count().reset_index(drop=False)
)
df_grouped["SUM"] = df_grouped["TX_STATUS"].cumsum()
df_grouped = df_grouped[["BLOCK_TIMESTAMP", "SUM"]]
df_grouped.set_index("BLOCK_TIMESTAMP", inplace=True)

st.header("Spaceloot Transactions Over Time")
st.line_chart(data=df_grouped)

df_sent = (
    df_tx.groupby("SENDER", as_index=False)["TX_STATUS"]
    .count()
    .sort_values(by="TX_STATUS", ascending=False)
)
df_sent.rename(columns={"TX_STATUS": "SENT"}, inplace=True)

df_received = (
    df_tx.groupby("RECIPIENT", as_index=False)["TX_STATUS"]
    .count()
    .sort_values(by="TX_STATUS", ascending=False)
)
df_received.rename(columns={"TX_STATUS": "RECEIVED"}, inplace=True)

df_merge = df_claim.merge(df_sent, how="left", left_on="HOLDER", right_on="SENDER")
df_merge = df_merge.merge(
    df_received, how="left", left_on="HOLDER", right_on="RECIPIENT"
)

df_merge = df_merge[["HOLDER", "CLAIMED", "RECEIVED", "SENT"]]
df_merge.fillna(0, axis=0, inplace=True)
df_merge[["CLAIMED", "RECEIVED", "SENT"]] = df_merge[
    ["CLAIMED", "RECEIVED", "SENT"]
].astype(int)

df_merge["TOTAL"] = df_merge["CLAIMED"] + df_merge["RECEIVED"] - df_merge["SENT"]

st.header("Raw Transaction History")
st.write(df_merge)

# raw transactions
st.header("Raw Transaction History")
st.write(df_tx[["BLOCK_ID", "SENDER", "RECIPIENT", "TOKEN_ID"]])
