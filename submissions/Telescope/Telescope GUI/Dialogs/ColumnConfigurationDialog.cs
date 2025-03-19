using System.Text.Json;
using Terminal.Gui;

namespace Telescope_GUI;

public partial class MainView
{
	private Dialog? _columnConfigurationDialog;
	
	private async Task openColumnConfiguration()
	{
		_columnConfigurationDialog = new Dialog("Edit Columns")
		{
			Width = Dim.Percent(50),
			Height = Dim.Percent(50)
		};

		Button cancelButton = new Button("Close");
		cancelButton.Clicked += () => _columnConfigurationDialog.RequestStop();

		ListView listView = new ListView(_columns)
		{
			X = 0,
			Y = 0,
			Width = Dim.Fill(),
			Height = Dim.Fill(1)
		};

		listView.OpenSelectedItem += (e) =>
		{
			TextField columnNameField = new TextField(e.Value.ToString())
			{
				X = 1,
				Y = 1,
				Width = Dim.Fill(),
			};

			Dialog columEditDialog = new Dialog("Edit Column")
			{
				Width = Dim.Percent(25),
				Height = 6
			};

			Button saveButton = new Button("Save");
			saveButton.Clicked += () =>
			{
				if (_columns.SkipWhile((c, i) => i == e.Item || c != columnNameField.Text.ToString()).Any())
				{
					MessageBox.ErrorQuery("Error", "Column already exists.", "Ok");
					return;
				}

				if (string.IsNullOrWhiteSpace(columnNameField.Text.ToString()))
				{
					_columns.RemoveAt(e.Item);
					updateTable();
					columEditDialog.RequestStop();
					return;
				}

				_columns[e.Item] = columnNameField.Text.ToString();
				_appSettings.Columns = _columns;
				updateTable();
				File.WriteAllText("appsettings.json", JsonSerializer.Serialize(_appSettings));
				columEditDialog.RequestStop();
			};
			
			columnNameField.KeyUp += (e) =>
			{
				if (e.KeyEvent.Key == Key.Enter)
				{
					saveButton.OnClicked();
				}
			};

			columEditDialog.Add(columnNameField);
			columEditDialog.AddButton(saveButton);

			Application.Run(columEditDialog);
		};
		
		Button addButton = new Button("Add");
		addButton.Clicked += () =>
		{
			_columns.Add("New Column " + _columns.Count(c => c.StartsWith("New Column ")));
			listView.SelectedItem = _columns.Count - 1;
			listView.OnOpenSelectedItem();
		};

		Button removeButton = new Button("Remove");
		removeButton.Clicked += () =>
		{
			_columns.RemoveAt(listView.SelectedItem);
			updateTable();
		};

		Button removeAllButton = new Button("Remove All");
		removeAllButton.Clicked += () =>
		{
			_columns.Clear();
			updateTable();
		};

		Button moveUpButton = new Button("^");
		moveUpButton.Clicked += () =>
		{
			if (listView.SelectedItem == 0)
			{
				return;
			}

			(_columns[listView.SelectedItem], _columns[listView.SelectedItem - 1]) =
				(_columns[listView.SelectedItem - 1], _columns[listView.SelectedItem]);

			updateTable();

			listView.SelectedItem--;
			listView.SetFocus();
			updateTable();
		};

		Button moveDownButton = new Button("V");
		moveDownButton.Clicked += () =>
		{
			if (listView.SelectedItem == _columns.Count - 1)
			{
				return;
			}

			(_columns[listView.SelectedItem], _columns[listView.SelectedItem + 1]) =
				(_columns[listView.SelectedItem + 1], _columns[listView.SelectedItem]);
			listView.SelectedItem++;
			listView.SetFocus();
			updateTable();
		};

		_columnConfigurationDialog.Add(listView);
		_columnConfigurationDialog.AddButton(cancelButton);
		_columnConfigurationDialog.AddButton(addButton);
		_columnConfigurationDialog.AddButton(removeButton);
		_columnConfigurationDialog.AddButton(removeAllButton);
		_columnConfigurationDialog.AddButton(moveUpButton);
		_columnConfigurationDialog.AddButton(moveDownButton);
		
		Application.Run(_columnConfigurationDialog);
	}
}