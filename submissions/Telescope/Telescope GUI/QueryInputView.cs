using Terminal.Gui;

namespace Telescope_GUI;

public class QueryInputView : View
{
	public TextField? QueryField { get; private set; }
	private bool _enterDown;

	public QueryInputView(Func<Task> executeClick)
	{
		Label _queryLabel = new Label
		{
			Text = "Query:"
		};

		QueryField = new TextField
		{
			X = Pos.Right(_queryLabel) + 1,
			Y = Pos.Top(_queryLabel),
			Width = Dim.Fill(11)
		};
		
		QueryField.KeyDown += e =>
		{
			if (e.KeyEvent.Key == Key.Enter)
			{
				_enterDown = true;
			}
		};
		
		QueryField.KeyUp += async (KeyEventEventArgs e) =>
		{
			if (e.KeyEvent.Key != Key.Enter || !_enterDown)
			{
				return;
			}

			_enterDown = false;
			await executeClick();
		};
		
		Button _executeButton = new Button
		{
			Text = "Execute",
			X = Pos.Right(QueryField),
			Y = Pos.Top(QueryField),
			Width = 10
		};
		_executeButton.Clicked += async () => await executeClick();
		
		
		Add(_queryLabel);
		Add(QueryField);
		Add(_executeButton);
	}
	
	public void Disable()
	{
		QueryField.Enabled = false;
		QueryField.Text = "No container selected";
	}
	
	public void Enable(string query = "")
	{
		QueryField.Enabled = true;
		QueryField.Text = query;
	}
}