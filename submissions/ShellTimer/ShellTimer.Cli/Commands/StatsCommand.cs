using System.ComponentModel;
using ShellTimer.Cli.Data;
using ShellTimer.Cli.Data.Models;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

public class StatsCommand : Command<StatsCommand.Settings>
{
    private const int ContentWidth = 80;
    private const int SolvesPerPage = 10;
    private readonly Database _databaseService = new();

    public override int Execute(CommandContext context, Settings settings)
    {
        var pb = _databaseService.GetPersonalBest(settings.CubeSize);
        var ao5 = _databaseService.GetAverageOf(5, settings.CubeSize);
        var ao12 = _databaseService.GetAverageOf(12, settings.CubeSize);
        var ao100 = _databaseService.GetAverageOf(100, settings.CubeSize);

        var bestAo5 = GetBestAverage(5, settings.CubeSize);
        var bestAo12 = GetBestAverage(12, settings.CubeSize);
        var bestAo100 = GetBestAverage(100, settings.CubeSize);

        var allSolves = _databaseService.GetAllSolves(settings.CubeSize)
            .OrderByDescending(s => s.DateTime)
            .ToList();

        var totalPages = Math.Max(1, (int)Math.Ceiling(allSolves.Count / (double)SolvesPerPage));
        var currentPage = 0;
        var exit = false;

        while (!exit)
        {
            AnsiConsole.Clear();

            var pageSolves = GetPageSolves(allSolves, currentPage);

            AnsiConsole.Write(CreateHeader(settings.CubeSize));
            AnsiConsole.Write(CreateStatsTable(pb, ao5, ao12, ao100, bestAo5, bestAo12, bestAo100));
            AnsiConsole.Write(CreateSolvesChart(pageSolves, currentPage, totalPages));
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

    private Table CreateHeader(int cubeSize)
    {
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn($"[blue]Statistics for {cubeSize}x{cubeSize} Cube[/]").Centered());
        return table;
    }

    private Table CreateStatsTable(TimeSpan? pb, TimeSpan? ao5, TimeSpan? ao12, TimeSpan? ao100,
        TimeSpan? bestAo5, TimeSpan? bestAo12, TimeSpan? bestAo100)
    {
        var table = new Table().Border(TableBorder.Simple);
        table.AddColumn("Category");
        table.AddColumn("Current");
        table.AddColumn("Best");

        table.Centered();
        table.Border = TableBorder.HeavyEdge;

        table.AddRow(
            new Markup("[green]Personal Best[/]"),
            new Markup($"[green]{FormatStatTime(pb)}[/]"),
            new Markup("[grey]-[/]")
        );

        table.AddRow(
            new Markup("[cyan]Average of 5[/]"),
            new Markup($"[cyan]{FormatStatTime(ao5)}[/]"),
            new Markup($"[cyan]{FormatStatTime(bestAo5)}[/]")
        );

        table.AddRow(
            new Markup("[orange1]Average of 12[/]"),
            new Markup($"[orange1]{FormatStatTime(ao12)}[/]"),
            new Markup($"[orange1]{FormatStatTime(bestAo12)}[/]")
        );

        table.AddRow(
            new Markup("[magenta]Average of 100[/]"),
            new Markup($"[magenta]{FormatStatTime(ao100)}[/]"),
            new Markup($"[magenta]{FormatStatTime(bestAo100)}[/]")
        );

        return table;
    }

    private List<Solve> GetPageSolves(List<Solve> allSolves, int page)
    {
        return allSolves
            .Skip(page * SolvesPerPage)
            .Take(SolvesPerPage)
            .Reverse()
            .ToList();
    }

    private BarChart CreateSolvesChart(List<Solve> solves, int currentPage, int totalPages)
    {
        var chart = new BarChart()
            .Width(ContentWidth - 10)
            .Label($"[bold]Recent Solves (Page {currentPage + 1} of {totalPages})[/]")
            .CenterLabel();

        if (solves.Count == 0)
            return chart.AddItem("No solves yet", 0, Color.Grey);

        foreach (var solve in solves)
        {
            if (solve.Penalty == PenaltyType.DNF)
            {
                chart.AddItem("DNF", 0, Color.Red);
                continue;
            }

            var seconds = solve.EffectiveTime.TotalSeconds;
            var label = $"{FormatStatTime(solve.EffectiveTime)}";

            if (solve.Penalty == PenaltyType.PlusTwo)
                label += " (+2)";

            var color = GetSolveColor(solve);
            chart.AddItem(label, seconds, color);
        }

        return chart;
    }

    private TimeSpan? GetBestAverage(int count, int cubeSize)
    {
        var allSolves = _databaseService.GetAllSolves(cubeSize);
        if (allSolves.Count < count)
            return null;

        TimeSpan? bestAverage = null;

        for (var i = 0; i <= allSolves.Count - count; i++)
        {
            var window = allSolves.Skip(i).Take(count).ToList();

            var times = window.Select(s =>
                    s.Penalty == PenaltyType.DNF ? double.MaxValue :
                    s.Penalty == PenaltyType.PlusTwo ? s.TimeInMilliseconds + 2000 :
                    s.TimeInMilliseconds)
                .ToList();

            TimeSpan? average = null;

            if (count == 5 || count == 12)
            {
                var dnfCount = times.Count(t => t == double.MaxValue);
                if (dnfCount > 1)
                    continue;

                times = times.OrderBy(t => t).ToList();
                times.RemoveAt(0);
                times.RemoveAt(times.Count - 1);

                if (times.Any(t => t == double.MaxValue))
                    continue;

                average = TimeSpan.FromMilliseconds(times.Average());
            }
            else if (count == 100)
            {
                var dnfCount = times.Count(t => t == double.MaxValue);
                if (dnfCount > count / 20)
                    continue;

                times = times.OrderBy(t => t).ToList();
                var toRemove = count / 20;
                times = times.Skip(toRemove).Take(count - 2 * toRemove).ToList();

                if (times.Any(t => t == double.MaxValue))
                    continue;

                average = TimeSpan.FromMilliseconds(times.Average());
            }

            if (average.HasValue && (!bestAverage.HasValue || average.Value < bestAverage.Value))
                bestAverage = average;
        }

        return bestAverage;
    }

    private string FormatStatTime(TimeSpan? time)
    {
        if (!time.HasValue)
            return "-";

        if (time.Value == TimeSpan.MaxValue)
            return "DNF";

        return $"{time.Value.Minutes:D2}:{time.Value.Seconds:D2}.{time.Value.Milliseconds:D3}";
    }

    private Color GetSolveColor(Solve solve)
    {
        if (solve.Penalty == PenaltyType.DNF)
            return Color.Red;
        if (solve.Penalty == PenaltyType.PlusTwo)
            return Color.Yellow;

        var pb = _databaseService.GetPersonalBest(solve.CubeSize);
        if (!pb.HasValue || solve.EffectiveTime <= pb.Value)
            return Color.Green;

        if (solve.EffectiveTime.TotalMilliseconds <= pb.Value.TotalMilliseconds * 1.1)
            return Color.Cyan1;

        return Color.Blue;
    }

    public sealed class Settings : CommandSettings
    {
        [CommandOption("-c|--cube-size")]
        [Description("Size of the Rubik's cube (2, 3, 4, etc.)")]
        public int CubeSize { get; set; } = 3;
    }
}