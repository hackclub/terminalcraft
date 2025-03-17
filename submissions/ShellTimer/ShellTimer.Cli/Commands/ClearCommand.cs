using System.ComponentModel;
using ShellTimer.Cli.Data;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

internal sealed class ClearCommand : Command<ClearCommand.Settings>
{
    public override int Execute(CommandContext context, Settings settings)
    {
        if (!settings.Force)
        {
            var confirm =
                AnsiConsole.Confirm("Are you sure you want to clear all solve records? This action cannot be undone.",
                    false);
            if (!confirm)
            {
                AnsiConsole.MarkupLine("[yellow]Clear cancelled.[/]");
                return 0;
            }
        }

        var databaseService = new Database();
        var count = databaseService.ClearAllSolves();

        AnsiConsole.MarkupLine($"[green]Successfully cleared {count} solve records from the database.[/]");
        return 0;
    }

    public sealed class Settings : CommandSettings
    {
        [CommandOption("-f|--force")]
        [Description("Force clear without confirmation")]
        public bool Force { get; set; } = false;
    }
}