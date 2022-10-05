"""
Async api requesters

Requires session object, may use callback to process data
"""

import aiohttp


async def get_locations(
        session: aiohttp.ClientSession,
        api_key: str,
        query: str
):
    request = f"https://graphhopper.com/api/1/geocode?q={query}&key={api_key}"
    async with session.get(request) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
    return data


async def get_weather(
        session: aiohttp.ClientSession,
        api_key: str,
        latitude: float,
        longitude: float
):
    request = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    async with session.get(request) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
    return data


async def get_places(
        session: aiohttp.ClientSession,
        api_key: str,
        lang: str,
        radius: float,
        latitude: float,
        longitude: float
):
    request = "https://api.opentripmap.com/0.1/{}/places/radius?radius={}&lon={}&lat={}&apikey={}".format(
        lang, radius, longitude, latitude, api_key)

    async with session.get(request) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
    return data


async def get_place_desc(
        session: aiohttp.ClientSession,
        api_key: str,
        lang: str,
        place_id: str,
        callback
):
    request = f"https://api.opentripmap.com/0.1/{lang}/places/xid/{place_id}?apikey={api_key}"
    async with session.get(request) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
    return await callback(data)
