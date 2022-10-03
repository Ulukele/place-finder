import asyncio
import aiohttp
from rich.prompt import IntPrompt, Prompt, Confirm
from rich.console import Console
from rich.panel import Panel

from config import *
import utils

console = Console()


def fatal(message):
    console.print(f"[red]{message}")
    exit(1)


async def handle_location(data):
    hits = data['hits']
    console.print()
    console.rule("Searching results")
    for idx, hit in enumerate(hits):
        point = hit['point']

        title = f"[yellow][{idx}][/] [green]{hit['name']}"
        text = f"""
[purple]Coordinates[/]: ({point['lat']}, {point['lng']})
{hit['osm_type']} - {hit['osm_key']} - {hit['osm_value']}
"""
        panel = Panel.fit(text, title=title)
        console.print(panel)
    return hits


async def handle_weather(data):
    weather = data['weather'][0]
    temp = int(data['main']['temp'] - 273.0)
    feels_like = int(data['main']['feels_like'] - 273.0)

    text = f"""
{weather['main']}. {weather['description']}
[purple]Temperature[/]: {temp} °C
[purple]Feels like[/]: {feels_like} °C"""

    panel = Panel.fit(text, title="[blue]Weather")
    console.print(panel)


async def handle_places(data, session):
    features = data['features']

    console.rule("Searching results")

    places = []
    for feature in features:
        xid = feature['properties']['xid']
        # Do request and print result after
        places.append(
            utils.get_place_desc(session, OPEN_TRIP_MAP_API_KEY, "ru", xid, handle_place)
        )

    # Await all after
    await asyncio.gather(*places)


async def handle_place(data):
    name = data['name']
    if not name:
        name = "[red]???"
    address = data['address']
    keys = ['country', 'state', 'suburb', 'road', 'house_number']
    values = [address[key] for key in keys if key in address]
    kinds = '\n'.join(data['kinds'].split(','))

    info = ''
    if 'info' in data and 'desc' in data['info']:
        info = data['info']['descr']

    title = f"[green]{name}"
    text = f"""
[purple]Rate[/]: {data['rate']}
[purple]Address[/]: {', '.join(values)}
[purple]Info[/]: {info if info else '[red]No info provided[/]'}
[purple]Tags[/]:
{kinds}
    """
    panel = Panel.fit(text, title=title)
    console.print(panel)


async def main():
    async with aiohttp.ClientSession() as session:
        do_loop = True
        while do_loop:
            # Enter query
            geo_query = Prompt.ask("[yellow]Enter query")

            # Handle query
            locations_data = await utils.get_locations(session, GRAPH_HOPPER_API_KEY, geo_query)
            if locations_data is None:
                fatal("Error while get locations from api")
            hits = await handle_location(locations_data)

            # Choose location
            choices = list(map(str, range(len(hits))))
            location_idx = IntPrompt.ask("[yellow]Choose location", choices=choices, show_choices=False, default=0)

            # Get chosen location coordinates
            hit = hits[location_idx]
            lat = hit['point']['lat']
            lng = hit['point']['lng']

            # Get weather info
            weather_data = await utils.get_weather(session, OPEN_WEATHER_API_KEY, lat, lng)
            if weather_data is None:
                fatal("Error while get weather info from api")

            # Handle weather info
            await handle_weather(weather_data)

            # Handle searching places around
            radius = IntPrompt.ask("[yellow]Enter places searching radius", default=1000)
            places_data = await utils.get_places(session, OPEN_TRIP_MAP_API_KEY, "ru", radius, lat, lng)
            if places_data is None:
                fatal("Error while get places from api")

            # Print all places info async
            await handle_places(places_data, session)

            # Ask to do once more
            do_loop = Confirm.ask("Search one more?", default=False)


if __name__ == '__main__':
    asyncio.run(main())
