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


response = requests.get(
    url="https://randomearth.io/api/items?collection_addr=terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k&sort=price.asc&page=1&on_sale=1"
)

df = pd.DataFrame(response.json()["items"])
df_traits = pd.DataFrame([flatten(d) for d in df["traits"].to_list()])
df_rarity = pd.read_csv("GP Rarity Calculator.csv")

df_merge = pd.concat(
    [df, df_traits],
    axis=1,
)

df_merge.drop(columns="traits", inplace=True)

df_merge = df_merge.merge(df_rarity, on="name")

st.write(df_merge)


def display(col, row):
    col.markdown(
        f"""
    # {row['name']}
    ## Price: {row["price"] / 1_000_000} LUNA
    ## Ranking: {row["ranking"]}
    ## Link: [RandomEarth]({row["token_id_x"]})

    ![]({row["src"]})
    """
    )


col1, col2, col3 = st.columns(3)

for i, row in df_merge.iterrows():
    if i // 1:
        display(col1, row)
    elif i // 2:
        display(col2, row)
    else:
        display(col3, row)
