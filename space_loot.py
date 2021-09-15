import streamlit as st
import plotly.express as px
import pandas as pd

query_id = "0e1550c8-3724-4d93-84e5-76b68b3956d4"

# load data into a DataFrame
df = pd.read_json(
    f"https://api.flipsidecrypto.com/api/v2/queries/{query_id}/data/latest",
    convert_dates=["BLOCK_TIMESTAMP"],
)

# Basic setup and app layout
# st.set_page_config(layout="wide")
st.title("Spaceloot Dashboard")

st.header("Transactions Log")
st.write(df[["BLOCK_ID", "SENDER", "RECIPIENT", "TOKEN_ID"]])

df.set_index("BLOCK_TIMESTAMP", inplace=True)
df_grouped = df["TX_STATUS"].groupby(pd.Grouper(freq="H")).count()

st.header("Spaceloot Transactions Per Hour")
st.line_chart(data=df_grouped)

print(df.info())
