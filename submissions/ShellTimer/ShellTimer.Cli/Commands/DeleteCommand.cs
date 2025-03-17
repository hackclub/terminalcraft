using System.ComponentModel;
using ShellTimer.Cli.Data;
using ShellTimer.Cli.Data.Models;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

public class DeleteCommand : Command<DeleteCommand.Settings>
{
    private const int ContentWidth = 80;
    private readonly Database _databaseService = new();

    public override int Execute(CommandContext context, Settings settings)
    {
        var solve = _databaseService.GetSolveById(settings.Id);

        if (solve == null)
        {
            AnsiConsole.Clear();
            AnsiConsole.Write(CreateHeader());
            AnsiConsole.Write(new Markup($"[red]Solve with ID {settings.Id} not found.[/]").Centered());
            AnsiConsole.Write(new Rule().RuleStyle("grey"));
            AnsiConsole.Write(new Markup("[grey]Press any key to return...[/]").Centered());
            Console.ReadKey(true);
            return 1;
        }

        AnsiConsole.Clear();
        AnsiConsole.Write(CreateHeader());
        DisplaySolveInfo(solve);

        var confirmed = settings.Force ||
                        AnsiConsole.Confirm("[yellow]Are you sure you want to delete this solve?[/]", false);

        if (confirmed)
        {
            _databaseService.DeleteSolve(settings.Id);

            AnsiConsole.Clear();
            AnsiConsole.Write(CreateHeader());
            AnsiConsole.Write(new Markup("[green]Solve was successfully deleted.[/]").Centered());
        }
        else
        {
            AnsiConsole.Clear();
            AnsiConsole.Write(CreateHeader());
            AnsiConsole.Write(new Markup("[yellow]Deletion cancelled.[/]").Centered());
        }

        AnsiConsole.Write(new Rule().RuleStyle("grey"));
        AnsiConsole.Write(new Markup("[grey]Press any key to return...[/]").Centered());
        Console.ReadKey(true);
        return 0;
    }

    private Table CreateHeader()
    {
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn("[blue]Delete Solve[/]").Centered());
        return table;
    }

    private void DisplaySolveInfo(Solve solve)
    {
        var table = new Table().Border(TableBorder.Simple);
        table.AddColumn("Property");
        table.AddColumn("Value");

        table.Centered();
        table.Border = TableBorder.HeavyEdge;

        var timeText = solve.Penalty == PenaltyType.DNF
            ? "DNF"
            : $"{solve.EffectiveTime.Minutes:D2}:{solve.EffectiveTime.Seconds:D2}.{solve.EffectiveTime.Milliseconds:D3}";

        var penaltyText = solve.Penalty switch
        {
            PenaltyType.None => "None",
            PenaltyType.PlusTwo => "+2",
            PenaltyType.DNF => "DNF",
            _ => "None"
        };

        table.AddRow(new Markup("[blue]ID[/]"), new Markup($"{solve.Id}"));
        table.AddRow(new Markup("[blue]Time[/]"), new Markup($"{timeText}"));
        table.AddRow(new Markup("[blue]Date[/]"), new Markup($"{solve.DateTime:yyyy-MM-dd HH:mm}"));
        table.AddRow(new Markup("[blue]Cube Size[/]"), new Markup($"{solve.CubeSize}x{solve.CubeSize}"));
        table.AddRow(new Markup("[blue]Penalty[/]"), new Markup($"{penaltyText}"));
        table.AddRow(new Markup("[blue]Scramble[/]"), new Markup($"{solve.Scramble}"));

        AnsiConsole.Write(table);
    }

    public sealed class Settings : CommandSettings
    {
        [CommandArgument(0, "<id>")]
        [Description("ID of the solve to delete")]
        public int Id { get; set; }

        [CommandOption("-f|--force")]
        [Description("Force delete without confirmation")]
        public bool Force { get; set; } = false;
    }
}