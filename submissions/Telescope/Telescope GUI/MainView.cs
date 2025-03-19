using System.Data;
using System.Text.Json;
using Microsoft.Azure.Cosmos;
using Microsoft.CSharp.RuntimeBinder;
using Telescope;
using Terminal.Gui;

namespace Telescope_GUI;

public partial class MainView : Window
{
	private MenuBar _menuBar;
	private QueryInputView _queryInputView;

	private bool _loading;

	private DataTable _dt;
	private TableView _resultsTable;
	private ContextMenu _tableContextMenu;
	private bool _updating;

	private CosmosApiWrapper _cosmosApiWrapper;
	private NavigatorBar _navigatorBar;
	private AppSettings _appSettings;

	private List<string> _columns;

	public MainView()
	{
		initializeComponent();
	}

	private void initializeComponent()
	{
		#region Load settings

		try
		{
			_appSettings = JsonSerializer.Deserialize<AppSettings>(File.ReadAllText("appsettings.json"));
		}
		catch
		{
			_appSettings = new AppSettings();
		}

		_cosmosApiWrapper = new CosmosApiWrapper();
		_cosmosApiWrapper.PageSize = _appSettings.Preferences.PageSize;

		_columns = _appSettings.Columns;

		try
		{
			if (_appSettings.AccountEndpoint is not null && _appSettings.AccountKey is not null)
			{
				_cosmosApiWrapper.SetCredentials(_appSettings.AccountEndpoint, _appSettings.AccountKey);
			}

			if (_appSettings.SelectedDatabase is not null)
			{
				_cosmosApiWrapper.SelectDatabase(_appSettings.SelectedDatabase);
			}

			if (_appSettings.SelectedContainer is not null)
			{
				_cosmosApiWrapper.SelectContainer(_appSettings.SelectedContainer);
			}
		}
		catch
		{
			// ignored
		}

		updateTitle();

		#endregion

		#region Components

		Width = Dim.Fill();
		Height = Dim.Fill();

		_menuBar = new MenuBar
		{
			Menus =
			[
				new MenuBarItem("_File",
				[
					new MenuItem("_Configure CosmosDB credentials", "", () => openCredentialConfiguration()),
					new MenuItem("_Select Database", "", async () => await openDatabaseSelection()),
					new MenuItem("_Select Container", "", async () => await openContainerSelection()),
					new MenuItem("_Quit", "", () => Application.RequestStop())
				]),

				// new MenuBarItem("_Preferences", Array.Empty<MenuItem>()) TODO: Preferences
			]
		};

		_queryInputView = new QueryInputView(executeQuery)
		{
			X = 0,
			Y = Pos.Bottom(_menuBar) + 1,
			Width = Dim.Fill(),
			Height = 1
		};

		_dt = new DataTable();

		_resultsTable = new TableView
		{
			X = 0,
			Y = Pos.Bottom(_queryInputView) + 1,
			Width = Dim.Fill(),
			Height = Dim.Fill(1),
			Table = _dt,
			Style = new TableView.TableStyle
			{
				AlwaysShowHeaders = true
			}
		};

		_tableContextMenu = new ContextMenu
		{
			MenuItems = new MenuBarItem("",
			[
				new MenuItem("Edit columns", "", async () => await openColumnConfiguration()),
			])
		};

		_resultsTable.MouseClick += e =>
		{
			if (!e.MouseEvent.Flags.HasFlag(MouseFlags.Button3Clicked))
			{
				return;
			}

			_tableContextMenu.Position = new Point(e.MouseEvent.X, e.MouseEvent.Y);
			_tableContextMenu.Show();
		};

		_navigatorBar = new NavigatorBar
		{
			X = 0,
			Y = Pos.Bottom(_resultsTable),
			Width = Dim.Fill(),
			Height = 1
		};
		_navigatorBar.PageChanged += async (page) =>
		{
			if (_updating)
			{
				return;
			}

			tableLoading();

			if (page < _cosmosApiWrapper.Pages.Count)
			{
				updateTable();
				return;
			}

			_navigatorBar.Pages += await _cosmosApiWrapper.LoadMore() ? 1 : 0;
			updateTable();
		};

		updateQueryField(_appSettings.LastQuery);
		updateTable();
		Add(_menuBar, _queryInputView, _resultsTable, _navigatorBar);

		#endregion
	}

	private async Task executeQuery()
	{
		if (_loading)
		{
			return;
		}

		_loading = true;
		_navigatorBar.SetPage(0);
		_navigatorBar.Pages = 0;

		_appSettings.LastQuery = _queryInputView.QueryField.Text.ToString();
		await File.WriteAllTextAsync("appsettings.json", JsonSerializer.Serialize(_appSettings));

		tableLoading();

		try
		{
			bool morePages =
				await _cosmosApiWrapper.GetFirstPageByQueryAsync(_queryInputView.QueryField.Text.ToString());
			_navigatorBar.Pages = _cosmosApiWrapper.Pages.Count + (morePages ? 1 : 0);
		}
		catch (CosmosException e)
		{
			_dt.Rows.Clear();
			MessageBox.ErrorQuery("Error", e.Message, "Ok");
		}
		catch (ArgumentException e)
		{
			_dt.Rows.Clear();
			MessageBox.ErrorQuery("Error", e.Message, "Ok");
		}
		finally
		{
			updateTable();
			_loading = false;
		}
	}

	private void tableLoading()
	{
		_dt.Rows.Clear();

		if (_dt.Columns.Count == 0)
		{
			return;
		}

		_dt.Rows.Add("Loading");
	}

	private void updateTable()
	{
		_updating = true;
		_dt.Rows.Clear();
		_dt.Columns.Clear();

		foreach (string column in _columns)
		{
			_dt.Columns.Add(column);
		}

		if (_cosmosApiWrapper.Pages.Count <= _navigatorBar.CurrentPage)
		{
			_navigatorBar.SetPage(_cosmosApiWrapper.Pages.Count - 1);

			_dt.AcceptChanges();
			_resultsTable.Update();
			return;
		}

		foreach (dynamic entity in _cosmosApiWrapper.Pages[_navigatorBar.CurrentPage])
		{
			DataRow row = _dt.NewRow();

			foreach (string column in _columns)
			{
				try
				{
					row[column] = entity[column];
				}
				catch (RuntimeBinderException)
				{
					row[column] = "";
				}
			}

			_dt.Rows.Add(row);
		}

		_navigatorBar.UpdateButtons();
		_dt.AcceptChanges();
		_resultsTable.Update();
		_updating = false;
	}

	private void updateQueryField(string query = "")
	{
		if (_appSettings.SelectedContainer is null)
		{
			_queryInputView.Disable();
		}
		else
		{
			_queryInputView.Enable(query);
		}
	}

	private void updateTitle()
	{
		if (_appSettings.SelectedContainer is null)
		{
			if (_appSettings.SelectedDatabase is null)
			{
				Title = "Telescope";
				return;
			}

			Title = $"Telescope - {_appSettings.SelectedDatabase}";
			return;
		}

		Title = $"Telescope - {_appSettings.SelectedDatabase}/{_appSettings.SelectedContainer}";
	}

	protected override void Dispose(bool disposing)
	{
		if (disposing)
		{
			_cosmosApiWrapper.Dispose();
			_dt.Dispose();
		}

		base.Dispose(disposing);
	}
}