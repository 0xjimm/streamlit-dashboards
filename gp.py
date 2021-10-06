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

# remove high ranking floors
df_merge = df_merge[df_merge["ranking"] < mean]

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

# featured listings
f1, f2, f3 = st.columns(3)

featured = [
    {
        "name": "Galactic Punk #8491",
        "img": "https://cloudflare-ipfs.com/ipfs/QmQBjNjtSqkjKxN6UyEvD3G62mRjHWMToCnGKxRP9xT6wJ",
        "url": "https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_65632299485635998173393205398896215996",
        "rank": 563,
        "price": 10000,
    },
    {
        "name": "Galactic Punk #542",
        "img": "https://cloudflare-ipfs.com/ipfs/QmcKk891vg2vFGcNpYQKG3dq8RyGkbQq9M8rjXs6nr7SqK",
        "url": "https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_173147050430553848553565161311621655916",
        "rank": 679,
        "price": 450,
    },
    {
        "name": "Galactic Punk #8408",
        "img": "https://cloudflare-ipfs.com/ipfs/Qmf6D5EeMWbvuyVuN6g96kz19YK9C6zqBsCnDZNkgzvyy1",
        "url": "https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_88140778103769665125156188028733008500",
        "rank": 5470,
        "price": 150,
    },
    {
        "name": "Galactic Punk #7445",
        "img": "https://cloudflare-ipfs.com/ipfs/QmdcptZ94i9fTpcdd8GTbdYunUefgRpKA4jzxiXvGcjV5d",
        "url": "https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_24143141112080848145913303035941697837",
        "rank": 125,
        "price": 2500,
    },
    {
        "name": "Galactic Punk #6494",
        "img": "https://cloudflare-ipfs.com/ipfs/QmUobtNhb9CdL84NKzXTCU3BGBqAqBVZi2tMbadtceuLfn",
        "url": "https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_109618086436110522639007560686842199046",
        "rank": 1557,
        "price": 325,
    },
    {
        "name": "Galactic Punk #3918",
        "img": "https://cloudflare-ipfs.com/ipfs/QmVc7asKMdvrvQRtm9evCJpEC7Gb7Eqkeus9BCghXASgWr",
        "url": "https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_219192806697718739956888622052907525661",
        "rank": 2111,
        "price": 400,
    },
]

rand_feat = random.sample(featured, 3)

for feat, col in zip(rand_feat, st.columns(len(rand_feat))):
    with col:
        resp = requests.get(feat["img"])
        f1_image = Image.open(BytesIO(resp.content))
        st.image(f1_image)
        st.markdown(
            f"""
            **[{feat['name']}]({feat['url']})**
            <br>
            Ask: {feat['price']:,} Luna
            <br>
            Rank: {feat['rank']:,}
        
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


display_table()

# auto refresher
if secs:
    st_autorefresh(interval=secs * 1000, key="dataframerefresh")
