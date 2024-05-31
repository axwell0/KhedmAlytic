import asyncio
import os
import random
import json
from aiohttp import ClientSession
import pandas as pd

async def send(zone: str, session: ClientSession, apikey: str, zones: dict):
    async with session.get(f'https://geocode.maps.co/search?q={zone}&api_key={apikey}') as resp:
        x = await resp.text()
        if x != "[]":
            try:
                json_response = json.loads(x)[0]
                lon = json_response['lon']
                lat = json_response['lat']
                zones[zone] = {'Longitude': lon, "Latitude": lat}
            except:
                print('Error with Json')


async def get_coordinates(df: pd.DataFrame, n_zones: int = 50) -> pd.DataFrame:
    geocoding_apikeys = ["your_api_keys"]
    zones = {}
    async with ClientSession() as session:
        for item in df['Zone'].value_counts().head(n_zones).index:
            await send(item, session, random.choice(geocoding_apikeys), zones)
            await asyncio.sleep(1)
    data = [{'Zone': zone, 'Longitude': coords['Longitude'], 'Latitude': coords['Latitude']} for zone, coords in
            zones.items()]
    return pd.DataFrame(data)
