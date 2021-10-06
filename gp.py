import random
import requests
import numpy as np
import pandas as pd
import streamlit as st

from PIL import Image
from io import BytesIO
from flatten_json import flatten
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")

# sidebar information
st.sidebar.markdown(
    f"""
    ## Description
    This app seeks to help you find deals on your Galactic Punks!
    This app will scrape three pages, sort and filter by rarity.
    """
)
st.sidebar.header("Options")

page_start = int(
    st.sidebar.number_input(
        "Starting Page Number",
        min_value=1,
        value=1,
        help="Page to begin scraping.",
    )
)

secs = st.sidebar.number_input(
    "Autorefresh Timer", min_value=30, value=180, help="Input time in seconds"
)

responses = []
for i in range(page_start, page_start + 3, 1):
    response = requests.get(
        url=f"https://randomearth.io/api/items?collection_addr=terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k&sort=price.asc&page={i}&on_sale=1"
    )
    responses.append(response)

dfs = pd.DataFrame()
for response in responses:
    df = pd.DataFrame(response.json()["items"])
    dfs = pd.concat([dfs, df])

dfs.reset_index(drop=True, inplace=True)

dfs.drop_duplicates(subset="name", inplace=True)

df_traits = pd.DataFrame([flatten(d) for d in df["traits"].to_list()])
df_rarity = pd.read_csv("GP Rarity Calculator.csv")

df_merge = pd.concat(
    [dfs, df_traits],
    axis=1,
)

df_merge.drop(columns="traits", inplace=True)

df_merge = df_merge.merge(df_rarity, on="name")

df_merge.sort_values(by="ranking", ascending=True, inplace=True)

df_merge.reset_index(drop=True, inplace=True)

mean = df_merge["ranking"].mean()

st.markdown(
    """
    # Galactic Punks Floor Scraper
    ### Created by [@lejimmy](https://twitter.com/lejimmy)
    If you found this useful and would like to support more of this type of work, consider contributing to my wallet here: *terra1m3sl9qea92km6mqm02yqxfygn8g9acl8wzj6x7*
    """
)

st.header("Featured Listings")
st.markdown(
    "**DM [@lejimmy](https://twitter.com/lejimmy) for featured listing inquiries.**"
)

# open featured text file
with open("featured.txt") as f:
    lines = f.readlines()

# extract relevant information
featured = []
for line in lines:
    resp = requests.get(
        f"https://randomearth.io/api/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_{line.strip()}"
    )
    gp = resp.json()["item"]
    featured.append(
        {"name": gp["name"], "price": gp["price"], "slug": gp["slug"], "src": gp["src"]}
    )

# sample 3
rand_feat = random.sample(featured, 3)

# display featured punks
for feat, col in zip(rand_feat, st.columns(len(rand_feat))):
    with col:
        resp = requests.get(feat["src"])
        f1_image = Image.open(BytesIO(resp.content))
        rank = df_rarity[df_rarity["name"] == feat["name"]]["ranking"].values[0]
        st.image(f1_image)
        st.markdown(
            f"""
            **[{feat['name']}]({feat['src']})**
            <br>
            Ask: {feat['price'] / 1_000_000:,} Luna
            <br>
            Rank: {rank:,}
            """,
            unsafe_allow_html=True,
        )

st.header("Listings")
st.markdown(
    f"""
    **Floor Price:** {df_merge['price'].min() / 1_000_000:,} Luna
    <br>
    **Ranking Mean:** {int(mean):,}
    """,
    unsafe_allow_html=True,
)


def display_table():
    for df_chunk in np.array_split(df_merge, len(df_merge) // 6 + 1):

        for (i, row), col in zip(df_chunk.iterrows(), st.columns(len(df_chunk))):

            with col:
                st.image(Image.open(BytesIO(requests.get(row["src"]).content)))
                st.markdown(
                    f"""
                    **[{row["name"][14:]}](https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_{row["token_id_x"]})**
                    <br>
                    Ask: {row['price'] / 1_000_000:,} Luna
                    <br>
                    Rank: {row["ranking"]:,}
                    """,
                    unsafe_allow_html=True,
                )

    pass


# remove high ranking floors
df_merge = df_merge[df_merge["ranking"] < mean]

display_table()

# auto refresher
if secs:
    st_autorefresh(interval=secs * 1000, key="dataframerefresh")
