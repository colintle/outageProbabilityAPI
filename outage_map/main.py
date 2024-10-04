import click

from . import import_dss_cli
from . import get_weather_events_cli
from . import format_weather_cli
from . import generate_weather_impact_cli
from . import generate_outage_map_cli
from . import find_extreme_cli

cli = click.CommandCollection(sources=[
    import_dss_cli.IMPORT_DSS,
    get_weather_events_cli.GET_WEATHER_EVENTS,
    format_weather_cli.FORMAT_WEATHER,
    generate_weather_impact_cli.GENERATE_WEATHER_IMPACT,
    generate_outage_map_cli.GENERATE_OUTAGE_MAP,
    find_extreme_cli.FIND_EXTREME
])

if __name__ == '__main__':
    cli()