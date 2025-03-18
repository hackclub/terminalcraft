using System.Text.Json;

namespace ShellTimer.Cli.Services;

public class ConfigService
{
    private readonly string _configPath;
    private Config _config;

    public ConfigService()
    {
        _configPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "ShellTimer",
            "config.json"
        );

        EnsureConfigDirectoryExists();
        LoadConfig();
    }

    public string? GetServerUrl()
    {
        return _config.ServerUrl;
    }

    public void SetServerUrl(string url)
    {
        _config.ServerUrl = url;
        SaveConfig();
    }

    private void EnsureConfigDirectoryExists()
    {
        var directory = Path.GetDirectoryName(_configPath);
        if (!Directory.Exists(directory))
            Directory.CreateDirectory(directory!);
    }

    private void LoadConfig()
    {
        if (File.Exists(_configPath))
            try
            {
                var json = File.ReadAllText(_configPath);
                _config = JsonSerializer.Deserialize<Config>(json) ?? new Config();
            }
            catch
            {
                _config = new Config();
            }
        else
            _config = new Config();
    }

    private void SaveConfig()
    {
        var json = JsonSerializer.Serialize(_config, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(_configPath, json);
    }

    private class Config
    {
        public string? ServerUrl { get; set; }
    }
}