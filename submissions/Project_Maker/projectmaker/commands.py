import os
import click
import shutil
import subprocess
from .config import load_config

@click.command()
@click.argument("project_name")
@click.argument("type")
@click.option("--directory", "-d", default=".", help="Directory where the project will be created")
def create(project_name, type, directory):
    """Creates a project with a specific type"""
    
    ctx = click.get_current_context()
    
    if type == "web":
        ctx.invoke(create_web, project_name=project_name, directory=directory)
    elif type == "godot":
        ctx.invoke(create_godot, project_name=project_name, directory=directory)
    elif type == "nodejs":
        ctx.invoke(create_nodejs, project_name=project_name, directory=directory)
    elif type == "unity":
        ctx.invoke(create_unity, project_name=project_name, directory=directory)
    else:
        click.echo(f"Unknown type: {type}")

@click.command()
def create_web(project_name, directory):
    """Creates a basic Web Project"""

    config = load_config()
    project_path = os.path.join(directory, project_name)
    
    # Make sure to control which directory to use
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    else:
        click.echo("Directory already exists.")
        return    

    for file in config["project_templates"]["web"]["files"]:
        file_path = os.path.join(project_path, file)

        with open(file_path, "w+") as f:
            if file == "index.html":
                html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    
    <script src="script.js"></script>
</body>
</html>"""

                f.write(html_template)
            elif file == "README.md":
                f.write(f"{project_name} - Web Project")

    click.echo(f"Web project '{project_name}' created successfully.")

    #choice = click.prompt("Do you want to open VS Code? (Y/N): ", type=str, default="N")
    if click.confirm("Do you want to open VS Code?"):
        code_path = shutil.which("Code")
        if code_path is None:
            click.echo("Couldn't open with VS Code.")
        else:
            subprocess.run([code_path, project_path])


@click.command()
def create_godot(project_name, directory):
    """Creates a Godot 4.4 Project"""

    config = load_config()
    project_path = os.path.join(directory, project_name)
    
    # Make sure to control which directory to use
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    else:
        click.echo("Directory already exists.")
        return 
    
    for folder in config["project_templates"]["godot"]["folders"]:
        folder_path = os.path.join(project_path, folder)
        os.makedirs(folder_path)
    
    for file in config["project_templates"]["godot"]["files"]:
        file_path = os.path.join(project_path, file)
        with open(file_path, "w+") as f:
            if file == "project.godot":
                godot_template = f"""; Engine configuration file.
; It's best edited using the editor UI and not directly,
; since the parameters that go here are not all obvious.
;
; Format:
;   [section] ; section goes between []
;   param=value ; assign values to parameters

config_version=5

[application]

config/name="{project_name}"
config/features=PackedStringArray("4.4", "Forward Plus")
config/icon="res://icon.svg"

[rendering]

renderer/rendering_method="forward_plus"
"""

                f.write(godot_template)
            elif file == "README.md":
                f.write(f"{project_name} - Godot Project")
            elif file == ".gitatttributes":
                f.write("""# Normalize EOL for all files that Git considers text files.\n* text=auto eol=lf""")
            elif file == ".gitignore":
                f.write("# Godot 4+ specific ignores\n.godot/\n/android/")

    click.echo(f"Godot project '{project_name}' created successfully.")

@click.command()
def create_unity(project_name, directory):
    """Creates a Unity Project"""

    config = load_config()
    project_path = os.path.join(directory, project_name)
    
    # Make sure to control which directory to use
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    else:
        click.echo("Directory already exists.")
        return 
    
    for folder in config["project_templates"]["unity"]["folders"]:
        folder_path = os.path.join(project_path, folder)
        os.makedirs(folder_path)
    
    for file in config["project_templates"]["unity"]["files"]:
        file_path = os.path.join(project_path, file)
        with open(file_path, "w+") as f:
            if file == "README.md":
                f.write(f"{project_name} - Unity Project")
            if file == ".gitignore":
                unity_gitignore = """  
[Ll]ibrary/  
[Tt]emp/  
[Oo]bj/  
[Bb]uild/  
[Bb]uilds/  
[Ll]ogs/  
UserSettings/  
*.csproj  
*.unityproj  
*.sln  
*.suo  
*.tmp  
*.user  
*.userprefs  
*.pidb  
*.booproj  
"""
                f.write(unity_gitignore)
    
    click.echo(f"Unity project '{project_name}' created successfully.")


@click.command()
def create_nodejs(project_name, directory):
    """Creates a Node.js Project"""

    config = load_config()
    project_path = os.path.join(directory, project_name)
    
    npm_path = shutil.which("npm")
    if npm_path is None:
        click.echo("npm not found. Please install Node.js")
        return

    # Make sure to control which directory to use
    if not os.path.exists(project_path):
        os.makedirs(project_path)
    else:
        click.echo("Directory already exists.")
        return 
    

    for file in config["project_templates"]["node"]["files"]:
        file_path = os.path.join(project_path, file)
        with open(file_path, "w+") as f:
            if file == "index.js":
                app_template = """const express = require('express');
const app = express();
app.listen(3000, () => console.log('Server running on port 3000'));"""
                f.write(app_template)

    choice = click.prompt("Do you want to open VS Code? (Y/N): ", type=str, default="N")

    if choice.lower() == "y":
        code_path = shutil.which("Code")
        if code_path is None:
            click.echo("Couldn't open with VS Code.")
        else:
            subprocess.run([code_path, project_path])

    subprocess.run([npm_path, "init", "-y"], cwd=project_path)
    
    click.echo(f"Node.js project '{project_name}' created successfully.")