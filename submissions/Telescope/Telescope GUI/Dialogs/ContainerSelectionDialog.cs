using System.Text.Json;
using Microsoft.Azure.Cosmos;
using Terminal.Gui;

namespace Telescope_GUI;

public partial class  MainView
{
	private Dialog? _containerSelectionDialog;
	
	private async Task openContainerSelection()
	{
		_containerSelectionDialog = new Dialog("Select Container")
		{
			Width = Dim.Percent(25),
			Height = Dim.Percent(50)
		};

		Button cancelButton = new Button("Close");
		cancelButton.Clicked += () => _containerSelectionDialog.RequestStop();
		_containerSelectionDialog.AddButton(cancelButton);

		List<ContainerProperties> containers;
		
		try
		{
			containers = await _cosmosApiWrapper.ListContainers();
		}
		catch (InvalidOperationException e)
		{
			MessageBox.ErrorQuery("Error", e.Message, "Ok");
			return;
		}

		ListView listView = new ListView(containers.Select(c => c.Id).ToList())
		{
			X = 0,
			Y = 0,
			Width = Dim.Fill(),
			Height = Dim.Fill(1)
		};
		
		listView.OpenSelectedItem += async (e) =>
		{
			_appSettings.SelectedContainer = e.Value.ToString();
			_cosmosApiWrapper.SelectContainer(e.Value.ToString());
			updateTitle();
			updateQueryField();
			await File.WriteAllTextAsync("appsettings.json", JsonSerializer.Serialize(_appSettings));
			_containerSelectionDialog.RequestStop();
		};

		// TODO: Add select Button
		_containerSelectionDialog.Add(listView);
		Application.Run(_containerSelectionDialog);
	}
}