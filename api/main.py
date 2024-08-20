import click

from . import import_dss_cli


cli = click.CommandCollection(sources=[
    import_dss_cli.IMPORT_DSS
])

if __name__ == '__main__':
    cli()