using System.ComponentModel;
using System.Diagnostics;
using ShellTimer.Cli.Data;
using ShellTimer.Cli.Data.Enums;
using ShellTimer.Cli.Data.Models;
using ShellTimer.Shared.Support.Cube;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

internal sealed class TimerCommand : Command<TimerCommand.Settings>
{
    private const int ContentWidth = 80;

    private readonly Database _databaseService = new();
    private static TimerStatus Status { get; set; } = TimerStatus.Waiting;
    private static bool ExitRequested { get; set; }


    public override int Execute(CommandContext context, Settings settings)
    {
        while (Console.KeyAvailable)
            Console.ReadKey(true);

        var hasInspection = settings.InspectionTime > 0;
        var skipScrambleScreen = false;
        var nextScramble = ScrambleGenerator.GenerateScramble(settings.CubeSize, settings.ScrambleLength);

        var databaseService = new Database();

        while (true)
        {
            if (!skipScrambleScreen)
            {
                Status = TimerStatus.Waiting;
                ExitRequested = false;
                AnsiConsole.Clear();

                var scrambleTable = CreateScrambleTable(nextScramble, hasInspection);
                AnsiConsole.Write(scrambleTable);

                var key = Console.ReadKey(true);
                if (key.Key == ConsoleKey.Escape)
                    return 0;
                if (key.Key != ConsoleKey.Spacebar)
                    continue;
            }

            ExitRequested = false;
            AnsiConsole.Clear();

            Status = hasInspection ? TimerStatus.Inspection : TimerStatus.Started;

            var inspectionStopwatch = new Stopwatch();
            var stopwatch = new Stopwatch();

            using var cts = new CancellationTokenSource();
            ThreadPool.QueueUserWorkItem(_ => ListenForKeyBoardEvent(cts.Token), null);

            if (hasInspection)
            {
                RunInspectionPhase(inspectionStopwatch, settings.InspectionTime);
                if (ExitRequested)
                {
                    cts.Cancel();
                    return 0;
                }
            }

            stopwatch.Start();
            var timerTable = CreateTimerTable(stopwatch);

            AnsiConsole.Live(timerTable).Start(ctx =>
            {
                while (Status != TimerStatus.Stopped && !ExitRequested)
                {
                    UpdateTimerTable(timerTable, stopwatch);
                    ctx.Refresh();
                    Thread.Sleep(100);
                }
            });

            stopwatch.Stop();
            cts.Cancel();

            if (ExitRequested)
                return 0;

            var solve = new Solve
            {
                TimeInMilliseconds = stopwatch.ElapsedMilliseconds,
                CubeSize = settings.CubeSize,
                Scramble = nextScramble,
                DateTime = DateTime.Now
            };

            databaseService.SaveSolve(solve);

            nextScramble = ScrambleGenerator.GenerateScramble(settings.CubeSize, settings.ScrambleLength);

            var currentSolve = _databaseService.GetMostRecentSolve(settings.CubeSize);
            var resultTable = CreateResultTable(stopwatch.Elapsed, nextScramble, settings, currentSolve);
            AnsiConsole.Clear();
            AnsiConsole.Write(resultTable);

            while (true)
            {
                var key = Console.ReadKey(true);

                if (key.Key == ConsoleKey.Escape)
                    return 0;
                if (key.Key == ConsoleKey.Spacebar)
                {
                    skipScrambleScreen = true;
                    break;
                }

                if (currentSolve != null)
                {
                    if ((key.Key == ConsoleKey.D1 || key.Key == ConsoleKey.NumPad1) &&
                        currentSolve.Penalty != PenaltyType.PlusTwo)
                    {
                        _databaseService.UpdateSolvePenalty(currentSolve.Id, PenaltyType.PlusTwo);
                        currentSolve.Penalty = PenaltyType.PlusTwo;

                        resultTable = CreateResultTable(stopwatch.Elapsed, nextScramble, settings, currentSolve);
                        AnsiConsole.Clear();
                        AnsiConsole.Write(resultTable);
                    }
                    else if ((key.Key == ConsoleKey.D2 || key.Key == ConsoleKey.NumPad2) &&
                             currentSolve.Penalty != PenaltyType.DNF)
                    {
                        _databaseService.UpdateSolvePenalty(currentSolve.Id, PenaltyType.DNF);
                        currentSolve.Penalty = PenaltyType.DNF;

                        resultTable = CreateResultTable(stopwatch.Elapsed, nextScramble, settings, currentSolve);
                        AnsiConsole.Clear();
                        AnsiConsole.Write(resultTable);
                    }
                    else if ((key.Key == ConsoleKey.D3 || key.Key == ConsoleKey.NumPad3) &&
                             currentSolve.Penalty != PenaltyType.None)
                    {
                        _databaseService.UpdateSolvePenalty(currentSolve.Id, PenaltyType.None);
                        currentSolve.Penalty = PenaltyType.None;

                        resultTable = CreateResultTable(stopwatch.Elapsed, nextScramble, settings, currentSolve);
                        AnsiConsole.Clear();
                        AnsiConsole.Write(resultTable);
                    }
                }
            }
        }
    }

    private void RunInspectionPhase(Stopwatch inspectionStopwatch, int inspectionTime)
    {
        inspectionStopwatch.Start();
        var inspectionTable = CreateInspectionTable(inspectionStopwatch, inspectionTime);

        AnsiConsole.Live(inspectionTable).Start(ctx =>
        {
            while (Status != TimerStatus.Started &&
                   inspectionStopwatch.ElapsedMilliseconds <= inspectionTime * 1000 &&
                   !ExitRequested)
            {
                var inspectionGrid = CreateInspectionGrid(inspectionStopwatch, inspectionTime);
                inspectionTable.Rows.Update(0, 0, new Padder(inspectionGrid).PadTop(2).PadBottom(2));
                ctx.Refresh();
                Thread.Sleep(100);
            }
        });

        if (!ExitRequested)
            AnsiConsole.Clear();
        inspectionStopwatch.Stop();
    }

    private Table CreateScrambleTable(string scramble, bool hasInspection)
    {
        var table = new Table();
        table.AddColumn(new TableColumn("[blue]Scramble[/]").Centered());

        var grid = new Grid();
        grid.Width = ContentWidth;
        grid.AddColumn();
        grid.AddRow(new Markup($"[yellow]{scramble}[/]").Centered());

        var promptText = hasInspection
            ? "Press SPACE to start the inspection or ESC to exit..."
            : "Press SPACE to start the timer or ESC to exit...";
        grid.AddRow(new Markup($"[white]{promptText}[/]").Centered());

        table.AddRow(new Padder(grid).PadTop(2).PadBottom(2));
        table.Border = TableBorder.HeavyEdge;
        table.Width = ContentWidth;

        return table;
    }

    private Table CreateInspectionTable(Stopwatch stopwatch, int inspectionTime)
    {
        var inspectionTable = new Table();
        inspectionTable.AddColumn(new TableColumn("[green]Inspection[/]").Centered());
        inspectionTable.AddRow(new Padder(CreateInspectionGrid(stopwatch, inspectionTime)).PadTop(2).PadBottom(2));
        inspectionTable.Border = TableBorder.HeavyEdge;
        inspectionTable.Width = ContentWidth;
        return inspectionTable;
    }

    private Grid CreateInspectionGrid(Stopwatch stopwatch, int inspectionTime)
    {
        var grid = new Grid();
        grid.AddColumn();

        var progress = Math.Min(stopwatch.ElapsedMilliseconds / (inspectionTime * 1000.0), 1.0);
        grid.AddRow(new BreakdownChart().Width(ContentWidth)
            .AddItem("Inspection", 100 * progress, Color.Green)
            .AddItem("Remaining", 100 - 100 * progress, Color.Red)
            .HideTags()
            .HideTagValues());

        var formattedTime = FormatTimeSpan(stopwatch.Elapsed);
        grid.AddRow(new Padder(new Markup(formattedTime).Centered()).PadTop(1));
        grid.Expand = true;

        return grid;
    }

    private Table CreateTimerTable(Stopwatch stopwatch)
    {
        var table = new Table();
        table.AddColumn(new TableColumn("[green]Timer[/]").Centered());
        var formattedTime = FormatTimeSpan(stopwatch.Elapsed);
        table.AddRow(new TableRow([new Padder(new Markup(formattedTime)).PadTop(2).PadBottom(2)]));
        table.Border = TableBorder.HeavyEdge;
        table.Width = ContentWidth;
        return table;
    }

    private void UpdateTimerTable(Table table, Stopwatch stopwatch)
    {
        var formattedTime = FormatTimeSpan(stopwatch.Elapsed);
        table.Rows.Update(0, 0, new Padder(new Markup(formattedTime)).PadTop(2).PadBottom(2));
    }

    private Table CreateResultTable(TimeSpan elapsedTime, string nextScramble, Settings settings,
        Solve? currentSolve = null)
    {
        var table = new Table();
        table.AddColumn(new TableColumn("[blue]Results[/]").Centered());

        var grid = new Grid();
        grid.Width = ContentWidth;
        grid.AddColumn();

        string formattedTime;
        if (currentSolve != null && currentSolve.Penalty != PenaltyType.None)
        {
            if (currentSolve.Penalty == PenaltyType.DNF)
            {
                formattedTime = "DNF";
            }
            else
            {
                var penaltyTime = TimeSpan.FromMilliseconds(currentSolve.TimeInMilliseconds + 2000);
                formattedTime = $"{FormatTimeSpan(penaltyTime)} (+2)";
            }
        }
        else
        {
            formattedTime = FormatTimeSpan(elapsedTime);
        }

        grid.AddRow(new Markup($"[blue]{formattedTime}[/]").Centered());

        grid.AddEmptyRow();

        if (!ExitRequested && currentSolve != null)
        {
            if (currentSolve.Penalty == PenaltyType.None)
                grid.AddRow(new Markup("[grey]Press 1 for +2 penalty, 2 for DNF[/]").Centered());
            else
                grid.AddRow(new Markup("[grey]Press 3 to remove penalty[/]").Centered());
            grid.AddEmptyRow();
        }

        var pb = _databaseService.GetPersonalBest(settings.CubeSize);
        var ao5 = _databaseService.GetAverageOf(5, settings.CubeSize);
        var ao12 = _databaseService.GetAverageOf(12, settings.CubeSize);
        var ao100 = _databaseService.GetAverageOf(100, settings.CubeSize);

        var pbFormatted = FormatTimeSpan(pb);
        var ao5Formatted = FormatTimeSpan(ao5);
        var ao12Formatted = FormatTimeSpan(ao12);
        var ao100Formatted = FormatTimeSpan(ao100);

        var statsLine =
            $"[green]PB: {pbFormatted}[/] [cyan]Ao5: {ao5Formatted}[/] [orange1]Ao12: {ao12Formatted}[/] [magenta]Ao100: {ao100Formatted}[/]";
        grid.AddRow(new Markup(statsLine).Centered());

        grid.AddEmptyRow();
        grid.AddRow(new Markup("Next scramble:").Centered());
        grid.AddRow(new Markup($"[yellow]{nextScramble}[/]").Centered());
        grid.AddEmptyRow();
        grid.AddRow(new Markup("[white]Press SPACE to start again or ESC to exit[/]").Centered());

        table.AddRow(new Padder(grid).PadTop(2).PadBottom(2));
        table.Border = TableBorder.HeavyEdge;
        table.Width = ContentWidth;

        return table;
    }

    private string FormatTimeSpan(TimeSpan? time)
    {
        if (!time.HasValue)
            return "-";

        if (time.Value == TimeSpan.MaxValue)
            return "DNF";

        return $"{time.Value.Minutes:D2}:{time.Value.Seconds:D2}.{time.Value.Milliseconds:D3}";
    }

    private static void ListenForKeyBoardEvent(CancellationToken cancellationToken)
    {
        do
        {
            if (cancellationToken.IsCancellationRequested)
                return;

            if (Console.KeyAvailable)
            {
                var key = Console.ReadKey(true);

                if (key.Key == ConsoleKey.Escape)
                {
                    Status = TimerStatus.Stopped;
                    ExitRequested = true;
                    return;
                }

                if (key.Key == ConsoleKey.Spacebar)
                {
                    if (Status == TimerStatus.Inspection)
                    {
                        Status = TimerStatus.Started;
                    }
                    else
                    {
                        Status = TimerStatus.Stopped;
                        return;
                    }
                }
            }

            Thread.Sleep(10);
        } while (true);
    }

    public sealed class Settings : CommandSettings
    {
        [CommandOption("-c|--cube-size")]
        [Description("Size of the Rubik's cube (2, 3, 4, etc.)")]
        public int CubeSize { get; set; } = 3;

        [CommandOption("-i|--inspection-time")]
        [Description("Inspection time in seconds (0 to disable)")]
        public int InspectionTime { get; set; } = 15;

        [CommandOption("-s|--scramble-length")]
        [Description("Length of the scramble in moves")]
        public int? ScrambleLength { get; set; } = null;
    }
}