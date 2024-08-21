import click

from . import import_dss_cli
from . import get_weather_events_cli


cli = click.CommandCollection(sources=[
    import_dss_cli.IMPORT_DSS,
    get_weather_events_cli.GET_WEATHER_EVENTS
])

if __name__ == '__main__':
    cli()