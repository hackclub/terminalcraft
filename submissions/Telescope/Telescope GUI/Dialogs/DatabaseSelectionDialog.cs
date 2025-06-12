using System.Text.Json;
using Microsoft.Azure.Cosmos;
using Terminal.Gui;

namespace Telescope_GUI;

public partial class MainView
{
	private Dialog? _databaseSelectionDialog;

	private async Task openDatabaseSelection()
	{
		_databaseSelectionDialog = new Dialog("Select Database")
		{
			Width = Dim.Percent(25),
			Height = Dim.Percent(50)
		};

		Button cancelButton = new Button("Cancel");
		cancelButton.Clicked += () => _databaseSelectionDialog.RequestStop();
		_databaseSelectionDialog.AddButton(cancelButton);
		_databaseSelectionDialog.Text = "Loading Databases... (If this takes too long, check your credentials)";


		// TODO: Use ListView

		_databaseSelectionDialog.Initialized += new EventHandler(async (_, _) =>
		{
			{
				try
				{
					List<DatabaseProperties> databases = await _cosmosApiWrapper.ListDatabases();

					ListView listView = new ListView(databases.Select(d => d.Id).ToList())
					{
						X = 0,
						Y = 0,
						Width = Dim.Fill(),
						Height = Dim.Fill(1)
					};

					listView.OpenSelectedItem += async (e) =>
					{
						_appSettings.SelectedDatabase = e.Value.ToString();
						_cosmosApiWrapper.SelectDatabase(e.Value.ToString());
						updateTitle();
						await File.WriteAllTextAsync("appsettings.json", JsonSerializer.Serialize(_appSettings));
						_databaseSelectionDialog.RequestStop();
					};

					_databaseSelectionDialog.Text = "";
					_databaseSelectionDialog.Add(listView);
				}
				catch (InvalidOperationException e)
				{
					MessageBox.ErrorQuery("Error", e.Message, "Ok");
					_databaseSelectionDialog.RequestStop();
				}
				catch (CosmosException e)
				{
					MessageBox.ErrorQuery("CosmosException",
										  "A CosmosException was thrown. Did you enter the correct credentials?\n" +
										  e.Message, "Ok");
					_databaseSelectionDialog.RequestStop();
				}
			}
		});
		
		Application.Run(_databaseSelectionDialog);
	}
}
