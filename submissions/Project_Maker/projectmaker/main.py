import click

from .commands import create

@click.group()
def cli():
    """ProjectMaker: CLI Tool for creating project templates"""
    pass

cli.add_command(create)

if __name__ == "__main__":
    cli()