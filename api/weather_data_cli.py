import click
import os

@click.group(
    name="weather-data"
)
def WEATHER_DATA():
    pass

@WEATHER_DATA.command()
def weather_data():
    """Testing 2"""
    relative_path = os.getcwd()
    click.echo(f"It is working 2")
    click.echo(f"Current relative path: {relative_path}")