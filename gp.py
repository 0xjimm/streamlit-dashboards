import streamlit as st
import pandas as pd
import requests
from flatten_json import flatten
from PIL import Image
from io import BytesIO
import httpx
import asyncio
from streamlit_autorefresh import st_autorefresh

# st.set_page_config(layout="wide")
st.title("Galactic Punks")

st.sidebar.header("Options")
secs = st.sidebar.number_input(
    "Autorefresh Timer", min_value=10, value=60, help="Input time in seconds"
)
if secs:
    st_autorefresh(interval=secs * 1000, key="dataframerefresh")

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

col1, col2, col3 = st.columns(3)

df_merge.sort_values(by="ranking", ascending=True, inplace=True)

df_merge.reset_index(drop=True, inplace=True)


async def get_images():
    async with httpx.AsyncClient() as client:

        for i, row in df_merge.iterrows():
            url = row["src"]
            resp = await client.get(url)
            df_merge.loc[i, "image"] = resp.content


asyncio.run(get_images())


def display_table():
    for i, row in df_merge.iterrows():

        cols = st.columns(5)
        cols[0].image(Image.open(BytesIO(row["image"])))
        cols[1].write(row["name"])
        cols[1].write(f"Price: {row['price'] / 1_000_000} LUNA")
        cols[2].write(f'Ranking: {row["ranking"]}')
        cols[2].markdown(
            f'[Link](https://randomearth.io/items/terra103z9cnqm8psy0nyxqtugg6m7xnwvlkqdzm4s4k_{row["token_id_x"]})'
        )

    pass


display_table()
