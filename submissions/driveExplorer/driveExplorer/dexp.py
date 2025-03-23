from __future__ import annotations
import os.path
import json
import io
import click
from click import secho

import setuptools


import typing
if typing.TYPE_CHECKING:
    from collections.abc import Iterable
import urwid

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload


SCOPES = ["https://www.googleapis.com/auth/drive"]

@click.group()
def cli():
    pass
  
if not os.path.exists("credentials.json"):
  with open("credentials.json", "w") as creds:
    creds.write('{"installed":{"client_id":"608244956902-uap2nm4p29akebhp8qevlmu6fbm969a3.apps.googleusercontent.com","project_id":"psyched-choir-448608-n5","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://localhost"]}}')

  
  
def signup():
  creds = None
  
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    
    with open("token.json", "w") as token:
      token.write(creds.to_json())
    
  return creds

@cli.command("setup", help="Create dexp folder in destination location")
@click.argument('folder', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def setup(folder):
  
  creds = signup()
  try:
    service = build("drive", "v3", credentials=creds)
    results = service.files().list(q= "mimeType = 'application/vnd.google-apps.folder' and name = 'dexp' and trashed = False", fields="files(id,name,trashed)").execute()
    items = results.get("files", [])

    secho(items)

    if len(items) > 1:
      return secho("More than one folder with the name 'dexp', please delete/rename them.", fg="yellow")

    if len(items) == 0:
      file_metadata = {
          "name": "dexp",
          "mimeType": "application/vnd.google-apps.folder",
      }
    
      file = service.files().create(body=file_metadata, fields="id").execute()
      secho(f'Folder ID: "{file.get("id")}".')
      with open("data.json", "w") as datafile:
        datafile.write(f'{{"id":"{file.get("id")}, "dir":"{os.path.abspath(folder).replace("\\", "/")}"}}')
      
    if len(items) == 1:
      with open("data.json", "w+") as datafile:
        datafile.write(f'{{"id":"{items[0].get("id")}", "dir":"{os.path.abspath(folder).replace("\\", "/")}"}}')
        
    with open("data.json", "r") as datafile:
      data = json.load(datafile)
      
      if not os.path.exists(folder.replace("\\", "/") + "/dexp"):
        os.mkdir(os.path.abspath(folder).replace("\\", "/") + "/dexp")
        secho(f"dexp folder created in {data["dir"]}!", fg="green")
      else:
        secho("dexp folder found, setting it as folder...", fg="yellow")
        
    return secho("Setup complete!", fg="green")

  except HttpError as error:
    secho(f"An error occurred: {error}")

@cli.command("save", help="Save the dexp folder to Drive")
def save():
    creds = signup()
    if not os.path.exists("data.json"):
        return secho("Please run <dexp setup> to set up the folder first", fg="red")
    with open("data.json", "r+") as datafile:
        data = json.load(datafile)
        try:
            path = data["dir"]
            folderid = data["id"]
        except:
            return secho("Error! Please try running <dexp setup>", fg="red")

    try:
        secho("saving...")
        service = build("drive", "v3", credentials=creds)
        for i in os.listdir(path + "/dexp"):
            itempath = os.path.join(path + "/dexp", i)
            if os.path.isdir(itempath):
                filemetadata = {"name": i, "mimeType": "application/vnd.google-apps.folder"}
                results = service.files().list(pageSize=1, fields="files(id, parents)", q=f"'{folderid}' in parents and trashed=false and name='{i}'").execute()
                files = results.get("files", [])
                if files:
                    fileid = files[0]["id"]
                    currentparents = ",".join(files[0]["parents"])
                    file = service.files().update(fileId=fileid, body=filemetadata, addParents=folderid, removeParents=currentparents, fields="id, parents").execute()
                else:
                    filemetadata["parents"] = [folderid]
                    file = service.files().create(body=filemetadata, fields="id").execute()
                secho(f"Folder '{i}' saved successfully!", fg="green")
            else:
                media = MediaFileUpload(itempath, mimetype="application/octet-stream")
                filemetadata = {"name": i}
                results = service.files().list(pageSize=1, fields="files(id, parents)", q=f"'{folderid}' in parents and trashed=false and name='{i}'").execute()
                files = results.get("files", [])
                if files:
                    fileid = files[0]["id"]
                    currentparents = ",".join(files[0]["parents"])
                    file = service.files().update(fileId=fileid, body=filemetadata, media_body=media, addParents=folderid, removeParents=currentparents, fields="id, parents").execute()
                else:
                    filemetadata["parents"] = [folderid]
                    file = service.files().create(body=filemetadata, media_body=media, fields="id").execute()
                secho(f"File '{i}' saved successfully!", fg="green")

    except HttpError as error:
        secho(f"An error occurred: {error}")

  
    
@cli.command("browse", help="Browse the dexp folder in Drive")
def browse():
  creds = signup()
  if not os.path.exists("data.json"):
    return secho("Please run <dexp setup> to set up the folder first", fg="red")
  with open("data.json", "r+") as datafile:
    data = json.load(datafile)
    path = data["dir"]
    folderid = data["id"]
    
  
  service = build("drive", "v3", credentials=creds)
  def getstruct(folder_id=folderid):
    def getfolderfiles(folder_id):
      try:
        
        results = service.files().list(q=f"'{folder_id}' in parents and trashed=false", fields="files(id, name, mimeType)").execute()
        # print(results)
        items = results.get("files", [])
        if not items:
          return []
        return items
      except HttpError as error:
        secho(f"Error :p {error}")
        return []
      
    def makestruct(folder_id):
      struct = {}
      items = getfolderfiles(folder_id)
      # print(items)
      for i in items:
        if i["mimeType"] == "application/vnd.google-apps.folder":
          # print("Folder!!")
          struct[i["name"]] = makestruct(i["id"])
        else:
          # print("not folder :/")
          struct[i["name"]] = i["id"]
      return struct
    
    
    return makestruct(folder_id)

  structure = getstruct(folderid)
  # print(structure.keys())
  
  def menu(title: str, choices_: Iterable[str]) -> urwid.ListBox:
    body = [urwid.Text(title), urwid.Divider()]
    # print(choices_)
    for i,j in choices_.items():
        if isinstance(j, dict):
          i = i + "/"
        button = urwid.Button(i)
        urwid.connect_signal(button, "click", item_chosen, j)
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

  def item_chosen(button: urwid.Button, choice) -> None:
    if isinstance(choice, dict):
        if not choice:
          main.original_widget = urwid.Filler(
                    urwid.Pile(
                        [
                            urwid.Text(f"Empty Folder! Press 'q' twice to exit!"),
                        ]
                    )
                )
        body = [urwid.Text("Folder"), urwid.Divider()]
        for i, j in choice.items():
            button = urwid.Button(i)
            urwid.connect_signal(button, "click", item_chosen, j)
            body.append(urwid.AttrMap(button, None, focus_map="reversed"))

        main.original_widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
    else:
        fileid = str(choice)
        try:
            file_metadata = service.files().get(fileId=fileid, fields="name").execute()
            file_name = file_metadata["name"]
            request = service.files().get_media(fileId=fileid)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                main.original_widget = urwid.Filler(
                    urwid.Pile(
                        [
                            urwid.Text(f"Downloading {int(status.progress() * 100)}%"),
                        ]
                    )
                )
            file.seek(0)
            with open(os.path.expanduser("~/Downloads") + "/" + file_name, "wb") as f:
                f.write(file.read())
            secho(f"File '{file_name}' downloaded successfully!", fg="green")
        except HttpError as error:
            secho(f"An error occurred: {error}")
        exit_program()


  def exit_program() -> None:
      raise urwid.ExitMainLoop()

  def inputhandler(key):
    if key in ("q","Q"):
      raise urwid.ExitMainLoop()
  
  main = urwid.Padding(menu("Your Drive", structure), left=2, right=2)
  top = urwid.Overlay(
      main,
      urwid.SolidFill("\N{MEDIUM SHADE}"),
      align=urwid.CENTER,
      width=(urwid.RELATIVE, 60),
      valign=urwid.MIDDLE,
      height=(urwid.RELATIVE, 60),
      min_width=20,
      min_height=9,
  )
  urwid.MainLoop(top, palette=[("reversed", "standout", "")], unhandled_input=inputhandler).run()

      

if __name__ == "__main__":
  cli()