import click

from .commands import create

class Help(click.Group):
    def format_help(self, ctx, formatter):
        click.echo("\nProjectMaker: CLI Tool for creating project templates\n")
        click.echo("Usage: projectmaker create [Project Name] [Type] [OPTION]\n")
        click.echo("Available types:")
        click.echo("    web: Creates a basic HTML/CSS/JS web project")
        click.echo("    godot: Creates a Godot project")
        click.echo("    unity: Creates a Unity project")
        click.echo("    nodejs: Creates a Node.js project\n")
        click.echo("Avalable options:")
        click.echo("    --directory or -d: Specify the directory where you want the project to be\n")
        click.echo("Have fun with your projects!")

@click.group(cls=Help)
def cli():
    pass

cli.add_command(create)

if __name__ == "__main__":
    cli()