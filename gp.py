import os
import random
import requests
import numpy as np
import pandas as pd
import streamlit as st

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

rarity_method = st.sidebar.selectbox(
    "Rarity Method",
    options=["Tero0x", "Official", "Wengzilla"],
)

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

# get proxy
def get_proxy_list(webshare_key):

    response = requests.get(
        "https://proxy.webshare.io/api/proxy/list/?page=1&countries=US",
        headers={"Authorization": f"Token {webshare_key}"},
    )

    proxy_list = response.json()["results"]

    return proxy_list


# select random proxy
def get_random_proxy(proxy_list):

    proxy = random.choice(proxy_list)

    return {
        "http": f'http://{proxy["username"]}:{proxy["password"]}@{proxy["proxy_address"]}:{proxy["ports"]["http"]}',
    }


# get proxy
proxy = get_random_proxy(get_proxy_list(os.environ["WEBSHARE_KEY"]))

responses = []
for i in range(page_start, page_start + 3, 1):
    response = requests.get(
        url=f"https://randomearth.io/api/items?collection_addr=terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k&sort=price.asc&page={i}&on_sale=1",
        proxies=proxy,
    )
    responses.append(response)

dfs = pd.DataFrame()
for response in responses:
    st.write(response)
    df = pd.DataFrame(response.json()["items"])
    dfs = pd.concat([dfs, df])

dfs.reset_index(drop=True, inplace=True)

dfs.drop_duplicates(subset="name", inplace=True)

df_traits = pd.DataFrame([flatten(d) for d in df["traits"].to_list()])

if rarity_method == "Wengzilla":
    df_rarity = pd.read_csv("Wengzilla.csv")
else:
    df_rarity = pd.read_csv("Tero0x.csv")

df_merge = pd.concat(
    [dfs, df_traits],
    axis=1,
)

df_rarity = df_rarity[["name", "ranking", "token_id"]]

df_merge.drop(columns="traits", inplace=True)

df_merge = df_merge.merge(df_rarity, on="name")


if rarity_method == "Official":
    rank_col = "rarity"
    df_merge.sort_values(by="rarity", ascending=False, inplace=True)
else:
    rank_col = "ranking"
    df_merge.sort_values(by="ranking", ascending=True, inplace=True)


df_merge.reset_index(drop=True, inplace=True)

mean = df_merge[rank_col].mean()

# clear from memory unused ranks
del (df, dfs, df_rarity, df_traits)

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
    lines = [tuple(map(str, i.split(","))) for i in f]

# shuffle list
random.shuffle(lines)

# extract relevant information
featured = []
for line, address in lines:
    resp = requests.get(
        f"https://randomearth.io/api/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_{line.strip()}"
    )
    gp = resp.json()["item"]
    owner = gp["user_addr"]
    if owner == address.strip():
        featured.append(
            {
                "name": gp["name"],
                "price": gp["price"],
                "slug": gp["slug"],
                "src": gp["src"],
                "rarity": gp["rarity"],
            }
        )
    else:
        print(f'Featured GP that is unsold: https://randomearth.io/items/{gp["slug"]}')

    if len(featured) >= 3:
        break

# display featured punks
for feat, col in zip(featured, st.columns(len(featured))):
    with col:
        col.image(feat["src"])

        # catch unlisted features
        try:
            price = f'{feat["price"] / 1_000_000:,} Luna'
        except:
            price = "Not listed"

        st.markdown(
            f"""
            **[{feat['name']}](https://randomearth.io/items/{feat['slug']})**
            <br>
            Ask: {price}
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
                st.image(row["src"])
                st.markdown(
                    f"""
                    **[{row["name"][14:]}](https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_{row["token_id_x"]})**
                    <br>
                    Ask: {row['price'] / 1_000_000:,} Luna
                    <br>
                    Rarity: {int(row[rank_col])}
                    """,
                    unsafe_allow_html=True,
                )

    pass


# remove high ranking floors
df_merge = df_merge[df_merge[rank_col] < mean]

display_table()

# auto refresher
if secs:
    st_autorefresh(interval=secs * 1000, key="dataframerefresh")
