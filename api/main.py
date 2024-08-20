import click

from . import import_dss_cli
from . import weather_data_cli


cli = click.CommandCollection(sources=[
    import_dss_cli.IMPORT_DSS,
    weather_data_cli.WEATHER_DATA
])

if __name__ == '__main__':
    cli()