import click
import os
import pandas as pd

@click.group(name="find-extreme")
def FIND_EXTREME():
    pass

@FIND_EXTREME.command()
@click.option('--input-path', type=click.Path(exists=True), required=True, help="Relative path to the input directory containing the folders of all distribution networks and its weather features")
def find_extreme(input_path):
    """Find the minimum and maximum values for each weather feature across all distribution networks."""

    minimum = {
        'temp': float("inf"), 
        'dwpt': float("inf"), 
        'rhum': float("inf"), 
        'prcp': float("inf"), 
        'snow': float("inf"), 
        'wdir': float("inf"), 
        'wspd': float("inf"), 
        'wpgt': float("inf"), 
        'pres': float("inf"), 
        'tsun': float("inf")
    }

    maximum = {
        'temp': -float("inf"), 
        'dwpt': -float("inf"), 
        'rhum': -float("inf"), 
        'prcp': -float("inf"), 
        'snow': -float("inf"), 
        'wdir': -float("inf"), 
        'wspd': -float("inf"), 
        'wpgt': -float("inf"), 
        'pres': -float("inf"), 
        'tsun': -float("inf")
    }

    for ds in os.listdir(input_path):
        ds_path = os.path.join(input_path, ds)
        if not os.path.isdir(ds_path):
            continue

        for weather_feature in os.listdir(ds_path):
            weather_feature_path = os.path.join(ds_path, weather_feature)
            if not os.path.isdir(weather_feature_path):
                continue

            for component in ["nodes", "edges"]:
                for weather_event in os.listdir(os.path.join(weather_feature_path, component)):
                    weather_event_path = os.path.join(weather_feature_path, component, weather_event)

                    if weather_event.startswith("m"):
                        os.remove(weather_event_path)
                        continue

                    df = pd.read_csv(os.path.join(weather_feature_path, component, weather_event))
                    maximum[weather_feature] = max(maximum[weather_feature], df.max().max())
                    minimum[weather_feature] = min(minimum[weather_feature], df.min().min())

    click.echo("Minimum values for weather features:")
    for feature, value in minimum.items():
        if value != float("inf"):
            click.echo(f"{feature}: {value}")

    click.echo("\nMaximum values for weather features:")
    for feature, value in maximum.items():
        if value != -float("inf"):
            click.echo(f"{feature}: {value}")

if __name__ == "__main__":
    FIND_EXTREME()