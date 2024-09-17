import click
import os
import pandas as pd
import warnings
from .util.NetworkFunctions import getWeatherByCoords, roundup, parseDate, parseTime, adjust_2400_to_next_day
from datetime import datetime

warnings.filterwarnings("ignore")

@click.group(name="format-weather")
def FORMAT_WEATHER():
    pass

@FORMAT_WEATHER.command()
@click.option('--events-file', type=click.Path(exists=True), required=True, help='Path to the CSV file containing weather events.')
@click.option('--nodelist', type=click.Path(exists=True), required=True, help='Path to the CSV file containing the nodelist.')
@click.option('--edgelist', type=click.Path(exists=True), required=True, help='Path to the CSV file containing the edgelist.')
@click.option('--output-path', type=click.Path(), required=True, help='Relative output path to save the results.')
@click.option('--features', type=click.Choice(['temp', 'dwpt', 'rhum', 'prcp', 'snow', 'wdir', 'wspd', 'wpgt', 'pres', 'tsun', 'coco'], case_sensitive=True), multiple=True, required=True, help='Weather features to process.')
def format_weather(events_file, nodelist, edgelist, output_path, features):
    """Based on weather events, find the weather features occurred at each node and edge in network."""
    
    # Ensure no duplicate features
    features = list(set(features))

    ###############################################################
                # NETWORK AND WEATHER PARAMETERS
    ###############################################################

    # Importing Nodes and Edges of Network
    nodes = pd.read_csv(nodelist)
    edges = pd.read_csv(edgelist)

    # Weather Event to collect data for
    weatherEvents = pd.read_csv(events_file)

    # Create directories for each selected feature
    node_dirs = {}
    edge_dirs = {}
    for feature in features:
        node_dir = os.path.join(output_path, f'{feature}/nodes/')
        edge_dir = os.path.join(output_path, f'{feature}/edges/')
        os.makedirs(node_dir, exist_ok=True)
        os.makedirs(edge_dir, exist_ok=True)
        node_dirs[feature] = node_dir
        edge_dirs[feature] = edge_dir

    ###############################################################
                # NODE WEATHER DATA COLLECTION LOOP
    ###############################################################

    # Loop through weather events
    for j in weatherEvents.index:
        # Determine start and end date of event 
        begin_date, begin_time = parseDate(weatherEvents['BEGIN_DATE'][j]), parseTime(roundup(weatherEvents['BEGIN_TIME'][j]))
        end_date, end_time = parseDate(weatherEvents['END_DATE'][j]), parseTime(roundup(weatherEvents['END_TIME'][j]))
        
        begin_date, begin_time = adjust_2400_to_next_day(begin_date, begin_time)
        end_date, end_time = adjust_2400_to_next_day(end_date, end_time)

        start = datetime.strptime(f"{begin_date} {begin_time}", "%Y-%m-%d %H%M")
        end = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H%M")
        
        # Initialize Node Event Lists for each feature
        event_data = {feature: [] for feature in features}

        # Loop through each node
        for i in nodes.index:
            print(f"{i}th node for {j}th event")
            
            # Grab node coordinates
            long, lat = eval(nodes["coords"][i])
            
            # Query metrostats for Weather Data
            timeframe = getWeatherByCoords(long, lat, start, end)
            
            # Append the data for each selected feature
            for feature in features:
                event_data[feature].append(timeframe[feature])

        # Convert Lists to dataframes and save to corresponding directories
        for feature in features:
            events_df = pd.DataFrame(event_data.get(feature))
            events_df.reset_index(drop=True, inplace=True)
            events_df.to_csv(os.path.join(node_dirs[feature], f'weatherEvent{j+1}.csv'), index=False)

    ###############################################################
                # EDGE WEATHER DATA COLLECTION LOOP
    ###############################################################

    # Grab the names of files in the folder for any feature
    fileNames = [f for f in os.listdir(node_dirs[features[0]]) if os.path.isfile(os.path.join(node_dirs[features[0]], f))]

    # Create an edge list from the loaded edge csv
    edgeList = []
    for i in range(len(edges)):
        edgeList.append([int(edges.iloc[i]["source"]), int(edges.iloc[i]["target"])])

    # Loop through each file in the folder
    for name in fileNames:
        edge_data = {feature: pd.DataFrame(columns=[feature]) for feature in features}

        # Load data for each feature and calculate the edge data
        for feature in features:
            feature_df = pd.read_csv(os.path.join(node_dirs[feature], name))

            for source, target in edgeList:
                edge_values = (feature_df.iloc[[source]].values + feature_df.iloc[[target]].values) / 2
                edge_data[feature] = pd.concat([edge_data[feature], pd.DataFrame(edge_values, columns=feature_df.columns)], ignore_index=True)

        # Save each dataframe in its corresponding directory
        for feature in features:
            events_df = pd.DataFrame(edge_data.get(feature))
            if feature in events_df.columns:
                events_df = events_df.drop(columns=[feature])
            events_df.to_csv(os.path.join(edge_dirs.get(feature), name), index=False)

if __name__ == "__main__":
    FORMAT_WEATHER()
