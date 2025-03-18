using System.ComponentModel;
using ShellTimer.Cli.Data;
using ShellTimer.Cli.Data.Models;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

public class ListCommand : Command<ListCommand.Settings>
{
    private const int ContentWidth = 80;
    private const int ItemsPerPage = 10;
    private readonly Database _databaseService = new();

    public override int Execute(CommandContext context, Settings settings)
    {
        List<Solve> solves;
        if (settings.CubeSize.HasValue)
            solves = _databaseService.GetAllSolves(settings.CubeSize.Value)
                .OrderByDescending(s => s.DateTime)
                .ToList();
        else
            solves = _databaseService.GetAllSolves()
                .OrderByDescending(s => s.DateTime)
                .ToList();

        // Check if there are any solves
        if (solves.Count == 0)
        {
            AnsiConsole.Clear();
            AnsiConsole.Write(CreateHeader(settings.CubeSize));
            AnsiConsole.Write(new Markup("[yellow]No solves found.[/]").Centered());
            AnsiConsole.Write(new Rule().RuleStyle("grey"));
            AnsiConsole.Write(new Markup("[grey]Press any key to return...[/]").Centered());
            Console.ReadKey(true);
            return 0;
        }

        var currentPage = 0;
        var totalPages = (int)Math.Ceiling(solves.Count / (double)ItemsPerPage);
        var exit = false;

        while (!exit)
        {
            AnsiConsole.Clear();
            AnsiConsole.Write(CreateHeader(settings.CubeSize));
            AnsiConsole.Write(CreateSolvesTable(solves, currentPage));
            AnsiConsole.Write(CreatePaginationInfo(currentPage, totalPages));
            AnsiConsole.Write(new Rule().RuleStyle("grey"));
            AnsiConsole.Write(new Markup("[grey]← → to navigate pages | ESC to exit[/]").Centered());

            var key = Console.ReadKey(true);
            switch (key.Key)
            {
                case ConsoleKey.LeftArrow:
                    if (currentPage > 0)
                        currentPage--;
                    break;
                case ConsoleKey.RightArrow:
                    if (currentPage < totalPages - 1)
                        currentPage++;
                    break;
                case ConsoleKey.Escape:
                    exit = true;
                    break;
            }
        }

        return 0;
    }

    private Table CreateHeader(int? cubeSize)
    {
        var title = cubeSize.HasValue
            ? $"[blue]Solve History for {cubeSize}x{cubeSize} Cube[/]"
            : "[blue]Solve History[/]";

        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn(title).Centered());
        return table;
    }

    private Table CreateSolvesTable(List<Solve> solves, int page)
    {
        var table = new Table().Border(TableBorder.HeavyEdge);
        table.AddColumn(new TableColumn("#").Centered());
        table.AddColumn(new TableColumn("Time").Centered());
        table.AddColumn(new TableColumn("Date").Centered());
        table.AddColumn(new TableColumn("Cube").Centered());
        table.AddColumn(new TableColumn("Penalty").Centered());
        table.AddColumn(new TableColumn("Scramble").Width(30));

        var startIndex = page * ItemsPerPage;
        var pageSolves = solves.Skip(startIndex).Take(ItemsPerPage).ToList();

        foreach (var solve in pageSolves)
        {
            var timeText = FormatStatTime(solve.EffectiveTime);
            var timeColor = GetTimeColor(solve);

            var dateText = solve.DateTime.ToString("yyyy-MM-dd HH:mm");

            table.AddRow(
                new Markup($"[grey]{solve.Id}[/]"),
                new Markup($"[{timeColor}]{timeText}[/]"),
                new Markup($"[grey]{dateText}[/]"),
                new Markup($"{solve.CubeSize}x{solve.CubeSize}"),
                new Markup(GetPenaltyMarkup(solve.Penalty)),
                new Markup($"[grey]{solve.Scramble}[/]")
            );
        }

        return table;
    }

    private Markup CreatePaginationInfo(int currentPage, int totalPages)
    {
        return new Markup($"[blue]Page {currentPage + 1} of {totalPages}[/]").Centered();
    }

    private string FormatStatTime(TimeSpan time)
    {
        if (time == TimeSpan.MaxValue)
            return "DNF";

        return $"{time.Minutes:D2}:{time.Seconds:D2}.{time.Milliseconds:D3}";
    }

    private string GetTimeColor(Solve solve)
    {
        if (solve.Penalty == PenaltyType.DNF)
            return "red";

        var pb = _databaseService.GetPersonalBest(solve.CubeSize);
        if (!pb.HasValue)
            return "green";

        if (solve.EffectiveTime <= pb.Value)
            return "green";

        if (solve.EffectiveTime.TotalMilliseconds <= pb.Value.TotalMilliseconds * 1.1)
            return "cyan1";

        return "blue";
    }

    private string GetPenaltyMarkup(PenaltyType penalty)
    {
        return penalty switch
        {
            PenaltyType.None => "[grey]-[/]",
            PenaltyType.PlusTwo => "[yellow]+2[/]",
            PenaltyType.DNF => "[red]DNF[/]",
            _ => "[grey]-[/]"
        };
    }

    public sealed class Settings : CommandSettings
    {
        [CommandOption("-c|--cube-size")]
        [Description("Size of the Rubik's cube (optional, shows all sizes if not specified)")]
        public int? CubeSize { get; set; } = null;
    }
}