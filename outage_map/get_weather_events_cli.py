import click
import pandas as pd
from geopy.geocoders import Nominatim
import requests
import urllib
from bs4 import BeautifulSoup

state_fips = {
    # State FIPS codes as provided
    "Alabama": "01",
    "Alaska": "02",
    "Arizona": "04",
    "Arkansas": "05",
    "California": "06",
    "Colorado": "08",
    "Connecticut": "09",
    "Delaware": "10",
    "District of Columbia": "11",
    "Florida": "12",
    "Georgia": "13",
    "Hawaii": "15",
    "Idaho": "16",
    "Illinois": "17",
    "Indiana": "18",
    "Iowa": "19",
    "Kansas": "20",
    "Kentucky": "21",
    "Louisiana": "22",
    "Maine": "23",
    "Maryland": "24",
    "Massachusetts": "25",
    "Michigan": "26",
    "Minnesota": "27",
    "Mississippi": "28",
    "Missouri": "29",
    "Montana": "30",
    "Nebraska": "31",
    "Nevada": "32",
    "New Hampshire": "33",
    "New Jersey": "34",
    "New Mexico": "35",
    "New York": "36",
    "North Carolina": "37",
    "North Dakota": "38",
    "Ohio": "39",
    "Oklahoma": "40",
    "Oregon": "41",
    "Pennsylvania": "42",
    "Rhode Island": "44",
    "South Carolina": "45",
    "South Dakota": "46",
    "Tennessee": "47",
    "Texas": "48",
    "Utah": "49",
    "Vermont": "50",
    "Virginia": "51",
    "Washington": "53",
    "West Virginia": "54",
    "Wisconsin": "55",
    "Wyoming": "56"
}

events = [
    "ALL",
    # List of events as provided
    "Astronomical Low Tide", "Avalanche", "Blizzard", "Coastal Flood", "Cold/Wind Chill",
    "Debris Flow", "Dense Fog", "Dense Smoke", "Drought", "Dust Devil", "Dust Storm",
    "Excessive Heat", "Extreme Cold/Wind Chill", "Flash Flood", "Flood", "Freezing Fog",
    "Frost/Freeze", "Funnel Cloud", "Hail", "Heat", "Heavy Rain", "Heavy Snow", "High Surf",
    "High Wind", "Hurricane (Typhoon)", "Ice Storm", "Lake-Effect Snow", "Lakeshore Flood",
    "Lightning", "Marine Hail", "Marine High Wind", "Marine Strong Wind", "Marine Thunderstorm Wind",
    "Rip Current", "Seiche", "Sleet", "Sneakerwave", "Storm Surge/Tide", "Strong Wind",
    "Thunderstorm Wind", "Tornado", "Tropical Depression", "Tropical Storm", "Tsunami",
    "Volcanic Ash", "Waterspout", "Wildfire", "Winter Storm", "Winter Weather"
]

def get_county(lat, lon):
    """Find the county for the given latitude and longitude using Geopy."""
    geolocator = Nominatim(user_agent="county_finder")
    location = geolocator.reverse((lat, lon), exactly_one=True)
    address = location.raw['address']
    
    county = address.get('county', 'County not found')
    return county.split()[0]

def fetch_counties_for_state(state):
    """Fetch the list of counties for the given state from NOAA."""
    state_fips_code = state_fips[state]
    url = f"https://www.ncdc.noaa.gov/stormevents/choosedates.jsp?statefips={state_fips_code}%2C{urllib.parse.quote(state.upper())}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    counties = {}
    select_tag = soup.find('select', {'name': 'county'})
    options = select_tag.find_all('option')

    odd = 1
    for option in options:
        value = option['value']
        name = option.text.strip()
        if value != "ALL":  # Skip the "-- All --" option
            counties[name.upper()] = odd  # Map county name to its index
            odd += 2
    return counties

@click.group(
    name="get-weather-events"
)
def GET_WEATHER_EVENTS():
    """Retrieve weather events from NOAA and save them as a CSV file."""
    pass

@GET_WEATHER_EVENTS.command()
@click.option('--state', type=click.Choice(list(state_fips.keys())), required=True,
              help="State for which to retrieve weather events.")
@click.option('--events', type=click.Choice(events), multiple=True, required=True,
              help="One or more weather events to filter by.")
@click.option('--nodelist', type=click.Path(exists=True), required=True,
              help="Relative path to the nodelist CSV file.")
@click.option('--start-date', type=str, required=True,
              help="Start date in YYYY-MM-DD format.")
@click.option('--end-date', type=str, required=True,
              help="End date in YYYY-MM-DD format.")
@click.option('--output-path', type=click.Path(), required=True,
              help="Relative path to save the output CSV file.")
def get_weather_events(state, events, nodelist, start_date, end_date, output_path):
    """Retrieve weather events for a specified state, events, and date range, 
    and save the result as a CSV file."""
    
    # Load the nodelist CSV
    data = pd.read_csv(nodelist)
    
    # Calculate the average latitude and longitude from the nodelist
    lo = 0
    la = 0
    for i in data.index:
        longitude, latitude = eval(data["coords"][i])
        lo += longitude
        la += latitude

    avg_lat = la / len(data.index)
    avg_lon = lo / len(data.index)
    
    # Get the county from the average latitude and longitude
    county = get_county(avg_lat, avg_lon).upper()

    # Fetch counties for the state and find the correct index
    counties = fetch_counties_for_state(state)
    county_index = counties.get(county, "1")  # Default to "1" if county not found

    # Format the county as needed
    county_formatted = f"{county}%3A{county_index}"
    
    state_fips_code = state_fips[state]
    events = [f"(Z) {event}" for event in events]
    event_type_params = "&".join([f"eventType={urllib.parse.quote_plus(event)}" for event in events])
    beginDate_mm, beginDate_dd, beginDate_yyyy = start_date.split("-")[1], start_date.split("-")[2], start_date.split("-")[0]
    endDate_mm, endDate_dd, endDate_yyyy = end_date.split("-")[1], end_date.split("-")[2], end_date.split("-")[0]

    # Construct the URL with the calculated county
    url = f"https://www.ncdc.noaa.gov/stormevents/csv?{event_type_params}&beginDate_mm={beginDate_mm}&beginDate_dd={beginDate_dd}&beginDate_yyyy={beginDate_yyyy}&endDate_mm={endDate_mm}&endDate_dd={endDate_dd}&endDate_yyyy={endDate_yyyy}&county={county_formatted}&hailfilter=0.00&tornfilter=0&windfilter=000&sort=DT&submitbutton=Search&statefips={state_fips_code}%2C{state.upper()}"

    response = requests.get(url)
    
    if response.status_code == 200:
        print("Request successful!")
        # Convert the response text to a CSV and save it
        with open(output_path, 'w') as file:
            file.write(response.text)
        print(f"Data saved to {output_path}")
    else:
        print(f"Request failed with status code {response.status_code}")

if __name__ == "__main__":
    GET_WEATHER_EVENTS()
