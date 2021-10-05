import streamlit as st
import pandas as pd
import requests
import numpy as np
from flatten_json import flatten
from PIL import Image
from io import BytesIO
from streamlit_autorefresh import st_autorefresh

# st.set_page_config(layout="wide")

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


def display_table():
    for df_chunk in np.array_split(df_merge, len(df_merge) // 4):

        for (i, row), col in zip(df_chunk.iterrows(), st.columns(len(df_chunk))):

            with col:
                st.image(Image.open(BytesIO(requests.get(row["src"]).content)))
                st.markdown(
                    f"""
                    [{row["name"][14:]}](https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_{row["token_id_x"]})
                    <br>
                    Ask: {row['price'] / 1_000_000} LUNA
                    <br>
                    Rank: {row["ranking"]}
                    """,
                    unsafe_allow_html=True,
                )

    pass


mean = df_merge["ranking"].mean()

# remove high ranking floors
df_merge = df_merge[df_merge["ranking"] < mean]

st.title("Galactic Punks Floor Scraper")
st.sidebar.markdown(
    f"""
    ## Description
    This app will scrape the bottom 3 floor pages, sort and filter by rarity.

    **Floor Price:** {df_merge['price'].min() / 1_000_000} LUNA

    **Floor Ranking Mean:** {int(mean)}
    """
)

st.header("Featured Listings")
st.markdown(
    "**DM [@lejimmy](https://twitter.com/lejimmy) for featured listing inquiries.**"
)

f1, f2, f3 = st.columns(3)
with f1:
    resp = requests.get(
        "https://cloudflare-ipfs.com/ipfs/QmQBjNjtSqkjKxN6UyEvD3G62mRjHWMToCnGKxRP9xT6wJ"
    )
    f1_image = Image.open(BytesIO(resp.content))
    st.image(f1_image)
    st.markdown(
        f"**[Galactic Punk #8491](terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_65632299485635998173393205398896215996)**"
    )


with f2:
    resp = requests.get(
        "https://cloudflare-ipfs.com/ipfs/QmUg9qnhLdXvRi4z57UvK3pAHLx2VeNwTfA1VfcaozPEnA"
    )
    f1_image = Image.open(BytesIO(resp.content))
    st.image(f1_image)
    st.markdown(
        f"**[Galactic Punk #9911](https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_174404845267200243382862455568157033455)**"
    )

with f3:
    resp = requests.get(
        "https://cloudflare-ipfs.com/ipfs/QmPC8FCvNvDV9FFLABwbGadBBfAiRfZYkW2u5WpNr6b1Bz"
    )
    f1_image = Image.open(BytesIO(resp.content))
    st.image(f1_image)
    st.markdown(
        f"**[Galactic Punk #10552](https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_14114733817112864020353362702172799429)**"
    )


st.header("Listings")
display_table()

# autorefresh
st.sidebar.header("Options")
secs = st.sidebar.number_input(
    "Autorefresh Timer", min_value=30, value=180, help="Input time in seconds"
)
if secs:
    st_autorefresh(interval=secs * 1000, key="dataframerefresh")
