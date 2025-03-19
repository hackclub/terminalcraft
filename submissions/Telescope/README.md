# About
Telescope is a tool that allows you to view (and in the future, also modify) entities in a CosmosDB.
It displays entities in a table, and allows the user to configure the displayed columns.

![img.png](img.png)

The UI is built using [Terminal.Gui](https://github.com/gui-cs/Terminal.Gui)

## Features
- Display entities in a table
- Configure displayed columns
- Pagination

### Future Features
- Bulk Delete
- Bulk Update

## How to use
- Download the [latest release](https://github.com/Schlafhase/Telescope/releases)
- In the application, enter your CosmosDB Credentials by clicking File>Configure CosmosDB credentials
- Click File>Select Database and select the database you want to view
- Click File>Select Container and select the container you want to view
- Enter your query and press Enter or click "Execute"
- Scroll through pages using the buttons at the bottom of the application
- Configure displayed columns by right-clicking the table and clicking "Edit Columns"
- To edit a column, double-click it

## How to run on Linux
- Make sure the .NET SDK is installed
- Clone the repo
- Navigate to the "Telescope GUI" folder
- Run `dotnet run`