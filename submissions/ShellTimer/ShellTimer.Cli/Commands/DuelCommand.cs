using System.ComponentModel;
using System.Diagnostics;
using Microsoft.AspNetCore.SignalR.Client;
using ShellTimer.Cli.Services;
using Spectre.Console;
using Spectre.Console.Cli;

namespace ShellTimer.Cli.Commands;

internal sealed class DuelCommand : Command<DuelCommand.Settings>
{
    public enum TimerStatus
    {
        Waiting,
        Inspection,
        Started,
        Stopped
    }

    private const int ContentWidth = 80;
    private readonly TaskCompletionSource<bool> _duelCancelledTcs = new();
    private readonly TaskCompletionSource<bool> _duelEndedTcs = new();
    private readonly TaskCompletionSource<bool> _duelStartedTcs = new();


    private HubConnection _connection = null!;
    private int _cubeSize;

    private string? _duelCode;
    private TaskCompletionSource<string> _duelCodeReceivedTcs = new();

    private TaskCompletionSource<bool> _duelReadyTcs = new();
    private int _inspectionTime;

    private bool _isWinner;
    private int _otherTime;
    private string? _scramble;
    private static TimerStatus Status { get; set; } = TimerStatus.Waiting;
    private static bool ExitRequested { get; set; }

    public override int Execute(CommandContext context, Settings settings)
    {
        var configService = new ConfigService();
        var serverUrl = configService.GetServerUrl();

        if (string.IsNullOrEmpty(serverUrl))
        {
            AnsiConsole.MarkupLine(
                "[red]Server URL not configured. Please run 'shelltimer config --set-url <url>' first.[/]");
            return 1;
        }

        AnsiConsole.Clear();
        AnsiConsole.Write(new Rule("[yellow]Rubik's Cube Duel[/]").RuleStyle("grey"));

        try
        {
            _connection = new HubConnectionBuilder()
                .WithUrl($"{serverUrl}/Duel")
                .WithAutomaticReconnect()
                .Build();

            SetupSignalRHandlers();

            AnsiConsole.Status()
                .Start("Connecting to server...", async ctx =>
                {
                    await _connection.StartAsync();
                    ctx.Status("Connected!");
                    await Task.Delay(500);
                });

            if (!string.IsNullOrEmpty(settings.Join))
            {
                _duelCode = settings.Join;
                return JoinExistingDuel().GetAwaiter().GetResult();
            }
            else
            {
                return CreateNewDuel(settings).GetAwaiter().GetResult();
            }
        }
        catch (Exception ex)
        {
            AnsiConsole.MarkupLine($"[red]Connection error: {ex.Message}[/]");
            return 1;
        }
        finally
        {
            if (_connection?.State == HubConnectionState.Connected)
                _connection.StopAsync().GetAwaiter().GetResult();
        }
    }

    private async Task<int> CreateNewDuel(Settings settings)
    {
        _duelCodeReceivedTcs = new TaskCompletionSource<string>();
        _duelReadyTcs = new TaskCompletionSource<bool>();

        await AnsiConsole.Status().StartAsync("Creating new duel...", async ctx =>
        {
            await _connection.InvokeAsync("CreateDuel", settings.InspectionTime, settings.CubeSize,
                settings.ScrambleLength);
            await _duelCodeReceivedTcs.Task;
        });

        AnsiConsole.Clear();
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn("[blue]Duel Created[/]").Centered());

        var grid = new Grid().Width(ContentWidth);
        grid.AddColumn();
        grid.AddRow(new Markup($"[green]Duel code: [bold]{_duelCode}[/][/]").Centered());
        grid.AddRow(new Markup($"[white]Cube size: {settings.CubeSize}x{settings.CubeSize}[/]").Centered());
        grid.AddRow(new Markup($"[white]Inspection time: {settings.InspectionTime} seconds[/]").Centered());
        grid.AddRow(new Markup("[white]Waiting for opponent to join...[/]").Centered());
        grid.AddRow(new Markup("[white]Press ESC to cancel[/]").Centered());

        table.AddRow(new Padder(grid));
        AnsiConsole.Write(table);

        using var cts = new CancellationTokenSource();
        var escapeTask = Task.Run(() =>
        {
            while (!cts.Token.IsCancellationRequested)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true);
                    if (key.Key == ConsoleKey.Escape)
                    {
                        ExitRequested = true;
                        return;
                    }
                }

                Thread.Sleep(10);
            }
        }, cts.Token);

        var completedTask = await Task.WhenAny(_duelReadyTcs.Task, _duelCancelledTcs.Task, escapeTask);
        await cts.CancelAsync();

        if (ExitRequested)
        {
            await _connection.InvokeAsync("ExitDuel", _duelCode);
            return 0;
        }

        if (completedTask == _duelCancelledTcs.Task)
        {
            DisplayDuelCancelledMessage("Duel cancelled");
            return 0;
        }

        return await RunDuelProcess();
    }

    private async Task<int> JoinExistingDuel()
    {
        var success = await AnsiConsole.Status()
            .StartAsync("Joining duel...", async _ =>
                await _connection.InvokeAsync<bool>("JoinDuel", _duelCode));

        if (!success)
        {
            AnsiConsole.MarkupLine(
                "[red]Failed to join duel. The code may be invalid or the duel no longer exists.[/]");
            return 1;
        }

        var completedTask = await Task.WhenAny(_duelReadyTcs.Task, _duelCancelledTcs.Task);

        if (completedTask == _duelCancelledTcs.Task)
        {
            DisplayDuelCancelledMessage("Duel cancelled");
            return 0;
        }

        return await RunDuelProcess();
    }

    private async Task<int> RunDuelProcess()
    {
        try
        {
            DisplayDuelInfo();

            await WaitForSpaceKey();

            if (ExitRequested)
                return 0;

            await _connection.InvokeAsync("ReadyForDuel", _duelCode);

            DisplayWaitingForOpponent();

            using var cts = new CancellationTokenSource();
            var escapeTask = Task.Run(() =>
            {
                while (!cts.Token.IsCancellationRequested)
                {
                    if (Console.KeyAvailable)
                    {
                        var key = Console.ReadKey(true);
                        if (key.Key == ConsoleKey.Escape)
                        {
                            ExitRequested = true;
                            return;
                        }
                    }

                    Thread.Sleep(10);
                }
            }, cts.Token);

            var completedTask = await Task.WhenAny(_duelStartedTcs.Task, _duelCancelledTcs.Task, escapeTask);
            await cts.CancelAsync();

            if (ExitRequested)
            {
                await _connection.InvokeAsync("ExitDuel", _duelCode);
                return 0;
            }

            if (completedTask == _duelCancelledTcs.Task)
            {
                DisplayDuelCancelledMessage("Opponent left the duel");
                return 0;
            }

            if (_inspectionTime > 0)
                await RunInspectionPhase();

            if (ExitRequested)
                return 0;

            var solveTime = await RunSolvePhase();

            if (ExitRequested)
                return 0;

            await _connection.InvokeAsync("FinishSolve", _duelCode, solveTime);
            DisplayWaitingForResults(solveTime);

            completedTask = await Task.WhenAny(_duelEndedTcs.Task, _duelCancelledTcs.Task);

            if (completedTask == _duelCancelledTcs.Task)
            {
                DisplayDuelCancelledMessage("Opponent left the duel");
                return 0;
            }

            DisplayFinalResults();

            return 0;
        }
        catch (Exception ex)
        {
            AnsiConsole.MarkupLine($"[red]Error during duel: {ex.Message}[/]");
            return 1;
        }
    }

    private void DisplayDuelCancelledMessage(string message)
    {
        AnsiConsole.Clear();
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn("[red]Duel Cancelled[/]").Centered());

        var grid = new Grid().Width(ContentWidth);
        grid.AddColumn();
        grid.AddRow(new Markup($"[red]{message}[/]").Centered());
        grid.AddRow(new Markup("[white]Press any key to exit...[/]").Centered());

        table.AddRow(new Padder(grid).PadTop(2).PadBottom(2));
        AnsiConsole.Write(table);

        Console.ReadKey(true);
    }

    private void DisplayDuelInfo()
    {
        AnsiConsole.Clear();
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn("[blue]Ready to Duel[/]").Centered());

        var grid = new Grid().Width(ContentWidth);
        grid.AddColumn();
        grid.AddRow(new Markup($"[green]Duel code: [bold]{_duelCode}[/][/]").Centered());
        grid.AddRow(new Markup($"[white]Cube size: {_cubeSize}x{_cubeSize}[/]").Centered());
        grid.AddRow(new Markup($"[white]Inspection time: {_inspectionTime} seconds[/]").Centered());
        grid.AddRow(new Markup($"[yellow]Scramble: {_scramble}[/]").Centered());
        grid.AddRow(new Markup("[white]Press SPACE when you're ready to start...[/]").Centered());

        table.AddRow(new Padder(grid));
        AnsiConsole.Write(table);
    }

    private void DisplayWaitingForOpponent()
    {
        AnsiConsole.Clear();
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn("[green]Waiting for Opponent[/]").Centered());

        var grid = new Grid().Width(ContentWidth);
        grid.AddColumn();
        grid.AddRow(new Markup("[yellow]You are ready![/]").Centered());
        grid.AddRow(new Markup("[white]Waiting for opponent to be ready...[/]").Centered());

        table.AddRow(new Padder(grid));
        AnsiConsole.Write(table);
    }

    private void DisplayWaitingForResults(int solveTime)
    {
        AnsiConsole.Clear();
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn("[blue]Waiting for Results[/]").Centered());

        var grid = new Grid().Width(ContentWidth);
        grid.AddColumn();
        grid.AddRow(
            new Markup($"[green]Your time: {FormatTimeSpan(TimeSpan.FromMilliseconds(solveTime))}[/]").Centered());
        grid.AddRow(new Markup("[white]Waiting for opponent to finish...[/]").Centered());

        table.AddRow(new Padder(grid));
        AnsiConsole.Write(table);
    }

    private void DisplayFinalResults()
    {
        AnsiConsole.Clear();
        var table = new Table().Border(TableBorder.HeavyEdge).Width(ContentWidth);
        table.AddColumn(new TableColumn("[blue]Duel Results[/]").Centered());

        var grid = new Grid().Width(ContentWidth);
        grid.AddColumn();

        var resultMessage = _isWinner
            ? "[green]You won![/]"
            : "[yellow]You lost![/]";

        grid.AddRow(new Markup(resultMessage).Centered());
        grid.AddRow(new Markup($"[white]Opponent's time: {FormatTimeSpan(TimeSpan.FromMilliseconds(_otherTime))}[/]")
            .Centered());
        grid.AddRow(new Markup("[white]Press any key to exit...[/]").Centered());

        table.AddRow(new Padder(grid));
        AnsiConsole.Write(table);

        Console.ReadKey(true);
    }

    private async Task<int> RunSolvePhase()
    {
        Status = TimerStatus.Started;
        ExitRequested = false;

        var stopwatch = new Stopwatch();
        stopwatch.Start();
        var timerTable = CreateTimerTable(stopwatch);

        using var solveCts = new CancellationTokenSource();
        ThreadPool.QueueUserWorkItem(_ => ListenForKeyBoardEvent(solveCts.Token), null);

        Task.Run(async () =>
        {
            await _duelCancelledTcs.Task;
            ExitRequested = true;
            Status = TimerStatus.Stopped;
        });

        AnsiConsole.Clear();
        AnsiConsole.Live(timerTable)
            .Start(ctx =>
            {
                while (Status != TimerStatus.Stopped && !ExitRequested)
                {
                    UpdateTimerTable(timerTable, stopwatch);
                    ctx.Refresh();
                    Thread.Sleep(100);
                }
            });

        stopwatch.Stop();
        solveCts.Cancel();

        if (_duelCancelledTcs.Task.IsCompleted)
        {
            DisplayDuelCancelledMessage("Opponent left the duel");
            return 0;
        }

        return (int)stopwatch.ElapsedMilliseconds;
    }

    private async Task RunInspectionPhase()
    {
        AnsiConsole.Clear();

        Status = TimerStatus.Inspection;
        var stopwatch = new Stopwatch();
        stopwatch.Start();
        var inspectionTable = CreateInspectionTable(stopwatch, _inspectionTime);

        using var inspectionCts = new CancellationTokenSource();
        ThreadPool.QueueUserWorkItem(_ => ListenForKeyBoardEvent(inspectionCts.Token), null);

        Task.Run(async () =>
        {
            await _duelCancelledTcs.Task;
            ExitRequested = true;
            Status = TimerStatus.Stopped;
        });

        AnsiConsole.Live(inspectionTable)
            .Start(ctx =>
            {
                while (Status == TimerStatus.Inspection &&
                       stopwatch.ElapsedMilliseconds <= _inspectionTime * 1000 &&
                       !ExitRequested)
                {
                    var inspectionGrid = CreateInspectionGrid(stopwatch, _inspectionTime);
                    inspectionTable.Rows.Update(0, 0, new Padder(inspectionGrid).PadTop(2).PadBottom(2));
                    ctx.Refresh();
                    Thread.Sleep(100);
                }
            });

        stopwatch.Stop();
        inspectionCts.Cancel();
    }

    private async Task WaitForSpaceKey()
    {
        var cancellationToken = new CancellationTokenSource();

        var cancellationTask = Task.Run(async () =>
        {
            await _duelCancelledTcs.Task;
            ExitRequested = true;
            cancellationToken.Cancel();
        });

        var keyPressTask = Task.Run(() =>
        {
            while (!cancellationToken.Token.IsCancellationRequested)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true);
                    if (key.Key == ConsoleKey.Escape)
                    {
                        ExitRequested = true;
                        return;
                    }

                    if (key.Key == ConsoleKey.Spacebar)
                        return;
                }

                Thread.Sleep(10);
            }
        }, cancellationToken.Token);

        await Task.WhenAny(keyPressTask, cancellationTask);
    }

    private void SetupSignalRHandlers()
    {
        _connection.On<string>("DuelCreated", duelCode =>
        {
            _duelCode = duelCode;
            _duelCodeReceivedTcs.TrySetResult(duelCode); // Complete this immediately so host can see the code
        });

        _connection.On<string, string, int, int>("DuelReady", (gameCode, scramble, cubeSize, inspectionTime) =>
        {
            _duelCode = gameCode;
            _scramble = scramble;
            _cubeSize = cubeSize;
            _inspectionTime = inspectionTime;
            _duelReadyTcs.TrySetResult(true);
        });

        _connection.On("DuelStarted", () => { _duelStartedTcs.TrySetResult(true); });

        _connection.On<bool, int>("DuelEnded", (isWon, otherTime) =>
        {
            _isWinner = isWon;
            _otherTime = otherTime;
            _duelEndedTcs.TrySetResult(true);
        });

        _connection.On("DuelCancelled", () =>
        {
            ExitRequested = true;
            Status = TimerStatus.Stopped;
            _duelCancelledTcs.TrySetResult(true);
        });
    }

    private Table CreateInspectionTable(Stopwatch stopwatch, int inspectionTime)
    {
        var table = new Table();
        table.AddColumn(new TableColumn("[green]Inspection[/]").Centered());
        table.AddRow(new Padder(CreateInspectionGrid(stopwatch, inspectionTime)).PadTop(2).PadBottom(2));
        table.Border = TableBorder.HeavyEdge;
        table.Width = ContentWidth;
        return table;
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
        table.AddRow(new Padder(new Markup(formattedTime).Centered()).PadTop(2).PadBottom(2));
        table.Border = TableBorder.HeavyEdge;
        table.Width = ContentWidth;
        return table;
    }

    private void UpdateTimerTable(Table table, Stopwatch stopwatch)
    {
        var formattedTime = FormatTimeSpan(stopwatch.Elapsed);
        table.Rows.Update(0, 0, new Padder(new Markup(formattedTime).Centered()).PadTop(2).PadBottom(2));
    }

    private string FormatTimeSpan(TimeSpan time)
    {
        return $"{time.Minutes:D2}:{time.Seconds:D2}.{time.Milliseconds:D3}";
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
        [CommandOption("-j|--join")]
        [Description("Duel code to join an existing duel")]
        public string? Join { get; set; }

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