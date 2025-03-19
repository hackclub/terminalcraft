using Terminal.Gui;

namespace Telescope_GUI;

public class NavigatorBar : View
{
	private readonly Button _previousButton;
	private readonly Button _firstButton;
	private readonly Button _nextButton;
	private readonly Label _pageLabel;
	
	private int _currentPage;

	public int CurrentPage
	{
		get => _currentPage;
		private set
		{
			_currentPage = value;
			PageChanged(value);
		}
	}
	
	public int Pages { get; set; }

	public event Action<int> PageChanged = delegate { };

	public NavigatorBar()
	{
		_previousButton = new Button("<") { X = Pos.Center() - 2, Y = 0 };
		_firstButton = new Button("<<") { X = Pos.Left(_previousButton) - 6, Y = 0 };
		_nextButton = new Button(">") { X = Pos.Right(_previousButton), Y = 0 };

		_firstButton.Clicked += () =>
		{
			CurrentPage = 0;
			UpdateButtons();
		};

		_previousButton.Clicked += () =>
		{
			CurrentPage--;
			UpdateButtons();
		};

		_nextButton.Clicked += () =>
		{
			CurrentPage++;
			UpdateButtons();
		};
		
		_pageLabel = new Label
		{
			X = 0,
			Y = 0,
			Width = Dim.Fill()
		};
		
		Add(_pageLabel, _previousButton, _firstButton, _nextButton);
		UpdateButtons();
	}

	public void UpdateButtons()
	{
		switch (CurrentPage)
		{
			case < 0:
				CurrentPage = 0;
				_previousButton.Enabled = false;
				_firstButton.Enabled = false;
				break;
			case 0:
				_previousButton.Enabled = false;
				_firstButton.Enabled = false;
				break;
			case > 0:
				_previousButton.Enabled = true;
				_firstButton.Enabled = true;
				break;
		}

		_nextButton.Enabled = CurrentPage < Pages - 1;
		_pageLabel.Text = $"Page {CurrentPage + 1}";
	}

	public void SetPage(int page)
	{
		CurrentPage = page < 0 ? 0 : page;
		UpdateButtons();
	}
}