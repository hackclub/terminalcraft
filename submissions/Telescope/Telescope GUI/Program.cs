using Telescope_GUI;
using Terminal.Gui;

Application.Init();

// TODO: Pages break when SELECT * FROM c is used

try
{
	Application.Run<MainView>();
}
finally
{
    Application.Shutdown();
}