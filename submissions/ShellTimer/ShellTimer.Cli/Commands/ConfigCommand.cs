using System.ComponentModel;
using ShellTimer.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

public class ConfigCommand : Command<ConfigCommand.Settings>
{
    public override int Execute(CommandContext context, Settings settings)
    {
        var configService = new ConfigService();

        if (settings.ShowUrl)
        {
            var url = configService.GetServerUrl();
            if (string.IsNullOrEmpty(url))
                AnsiConsole.MarkupLine("[yellow]Duel service URL is not configured.[/]");
            else
                AnsiConsole.MarkupLine($"[green]Duel service URL:[/] {url}");
            return 0;
        }

        if (!string.IsNullOrEmpty(settings.SetUrl))
        {
            configService.SetServerUrl(settings.SetUrl);
            AnsiConsole.MarkupLine($"[green]Duel service URL set to:[/] {settings.SetUrl}");
            return 0;
        }

        AnsiConsole.MarkupLine("[yellow]Please specify an option. Use --help for more information.[/]");
        return 1;
    }

    public sealed class Settings : CommandSettings
    {
        [CommandOption("--show-duel-service-url")]
        [Description("Show the current server URL")]
        public bool ShowUrl { get; set; }

        [CommandOption("--set-duel-service-url")]
        [Description("Set the server URL")]
        public string? SetUrl { get; set; }
    }
}