using System.ComponentModel;
using ShellTimer.Cli.Support.Cube;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

public class ScrambleCommand : Command<ScrambleCommand.Settings>
{
    private const int ContentWidth = 80;

    public override int Execute(CommandContext context, Settings settings)
    {
        AnsiConsole.Clear();

        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn($"[blue]{settings.CubeSize}x{settings.CubeSize} Cube Scrambles[/]").Centered());

        var grid = new Grid().Width(ContentWidth - 10);
        grid.AddColumn();

        for (var i = 0; i < settings.Count; i++)
        {
            var scramble = ScrambleGenerator.GenerateScramble(
                settings.CubeSize,
                settings.ScrambleLength ?? settings.CubeSize * 5
            );

            grid.AddRow($"[white]#{i + 1}:[/] [yellow]{scramble}[/]");
        }

        table.AddRow(new Padder(grid).PadTop(1).PadBottom(1));
        AnsiConsole.Write(table);

        AnsiConsole.Write(new Rule().RuleStyle("grey"));
        AnsiConsole.Write(new Markup("[grey]Press any key to exit...[/]").Centered());
        Console.ReadKey(true);

        return 0;
    }

    public sealed class Settings : CommandSettings
    {
        [CommandOption("-c|--cube-size")]
        [Description("Size of the Rubik's cube (2, 3, 4, etc.)")]
        public int CubeSize { get; set; } = 3;

        [CommandOption("-s|--scramble-length")]
        [Description("Length of the scramble in moves")]
        public int? ScrambleLength { get; set; } = null;

        [CommandOption("-n|--count")]
        [Description("Number of scrambles to generate")]
        public int Count { get; set; } = 5;
    }
}