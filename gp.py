import streamlit as st
import plotly.express as px
import statsmodels.api as sm
import pandas as pd
import json
import requests
from flatten_json import flatten
from PIL import Image

# st.set_page_config(layout="wide")
st.title("Galactic Punks")

responses = []
for i in range(3):
    response = requests.get(
        url=f"https://randomearth.io/api/items?collection_addr=terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k&sort=price.asc&page={i}&on_sale=1"
    )
    responses.append(response)

dfs = pd.DataFrame()
for response in responses:
    df = pd.DataFrame(response.json()["items"])
    dfs = pd.concat([dfs, df])

dfs.reset_index(drop=True, inplace=True)

df_traits = pd.DataFrame([flatten(d) for d in df["traits"].to_list()])
df_rarity = pd.read_csv("GP Rarity Calculator.csv")

df_merge = pd.concat(
    [dfs, df_traits],
    axis=1,
)

df_merge.drop(columns="traits", inplace=True)

df_merge = df_merge.merge(df_rarity, on="name")

# st.write(df_merge)


def display(col, row):
    col.markdown(
        f"""
    {row['name']}
    Price: {row["price"] / 1_000_000} LUNA
    Ranking: {row["ranking"]}
    Link: [RandomEarth]({row["token_id_x"]})
    """
    )


col1, col2, col3 = st.columns(3)

df_merge.sort_values(by="ranking", ascending=True, inplace=True)

for i, row in df_merge.iterrows():
    display(st, row)
