namespace Telescope_GUI;

public struct AppSettings
{
	public Preferences Preferences { get; set; } = new Preferences();
	
	public string? AccountEndpoint { get; set; } = null;
	public string? AccountKey { get; set; } = null;
	public string? SelectedDatabase { get; set; } = null;
	public string? SelectedContainer { get; set; } = null;
	
	public List<string> Columns { get; set; } = ["id"];
	
	public string LastQuery { get; set; } = "SELECT * FROM c";

	public AppSettings()
	{
		
	}
}

public struct Preferences
{
	public int PageSize { get; set; } = 25;
	public int MaxRetryCount { get; set; } = 100;
	public TimeSpan MaxRetryWaitTime { get; set; } = TimeSpan.FromMinutes(1);

	public Preferences()
	{
		
	}
}