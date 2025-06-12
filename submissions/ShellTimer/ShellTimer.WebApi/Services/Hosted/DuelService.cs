using System.Threading.Channels;
using Microsoft.AspNetCore.SignalR;
using ShellTimer.Shared.Support.Cube;
using ShellTimer.WebApi.Hubs;
using ShellTimer.WebApi.Models;

namespace ShellTimer.WebApi.Services.Hosted;

/// <summary>
///     Background service that processes duel events and manages duel lifecycle.
///     Handles communication between duel participants via SignalR.
/// </summary>
public class DuelService : BackgroundService
{
    private readonly ChannelReader<DuelEvent> _duelEvents;
    private readonly DuelManager _duelManager;
    private readonly IHubContext<DuelHub, IDuelHub> _hubContext;
    private readonly ILogger<DuelService> _logger;

    public DuelService(
        ChannelReader<DuelEvent> duelEvents,
        ILogger<DuelService> logger,
        IHubContext<DuelHub, IDuelHub> hubContext,
        DuelManager duelManager)
    {
        _duelEvents = duelEvents;
        _logger = logger;
        _hubContext = hubContext;
        _duelManager = duelManager;
    }

    /// <summary>
    ///     Executes the background service to process duel events.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token to stop the service.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    protected override async Task ExecuteAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Duel service started");

        await foreach (var @event in _duelEvents.ReadAllAsync(cancellationToken))
            try
            {
                await ProcessEventAsync(@event);
            }
            catch (Exception e)
            {
                _logger.LogError(e, "Error processing duel event: {EventType} for duel {DuelCode}",
                    @event.Type, @event.DuelCode);
            }
    }

    /// <summary>
    ///     Processes a duel event by dispatching to the appropriate handler.
    /// </summary>
    /// <param name="event">The duel event to process.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    private async Task ProcessEventAsync(DuelEvent @event)
    {
        switch (@event.Type)
        {
            case DuelEventType.DuelCreated:
                await HandleDuelCreatedAsync(@event);
                break;
            case DuelEventType.DuelJoined:
                await HandleDuelJoinedAsync(@event);
                break;
            case DuelEventType.PlayerReady:
                await HandlePlayerReadyAsync(@event);
                break;
            case DuelEventType.DuelExited:
                await HandleDuelExitedAsync(@event);
                break;
            case DuelEventType.SolveFinished:
                await HandleSolveFinishedAsync(@event);
                break;
        }
    }

    /// <summary>
    ///     Handles creation of a new duel.
    ///     Generates a scramble and notifies the host.
    /// </summary>
    /// <param name="event">The duel created event details.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    private async Task HandleDuelCreatedAsync(DuelEvent @event)
    {
        var scramble = ScrambleGenerator.GenerateScramble(
            @event.CubeSize!.Value,
            @event.ScrambleLength);

        if (_duelManager.TryCreateDuel(
                @event.DuelCode,
                @event.ConnectionId,
                @event.CubeSize!.Value,
                @event.InspectionTime!.Value,
                scramble))
            await _hubContext.Clients.Client(@event.ConnectionId).DuelCreated(@event.DuelCode);
    }

    /// <summary>
    ///     Handles a player joining an existing duel.
    ///     Notifies both players that the duel is ready to begin.
    /// </summary>
    /// <param name="event">The duel joined event details.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    private async Task HandleDuelJoinedAsync(DuelEvent @event)
    {
        if (!_duelManager.TryGetDuel(@event.DuelCode, out var duel) ||
            !_duelManager.TryJoinDuel(@event.DuelCode, @event.ConnectionId))
            return;

        await _hubContext.Clients
            .Clients([duel.HostConnectionId, @event.ConnectionId])
            .DuelReady(@event.DuelCode, duel.Scramble, duel.CubeSize, duel.InspectionTime);
    }

    /// <summary>
    ///     Handles a player marking themselves as ready.
    ///     When both players are ready, the duel starts.
    /// </summary>
    /// <param name="event">The player ready event details.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    private async Task HandlePlayerReadyAsync(DuelEvent @event)
    {
        if (!_duelManager.TryGetDuel(@event.DuelCode, out var duel) ||
            !_duelManager.SetPlayerReady(@event.DuelCode, @event.ConnectionId))
            return;

        await _hubContext.Clients
            .Clients([duel.HostConnectionId, duel.ChallengedConnectionId!])
            .DuelStarted();
    }

    /// <summary>
    ///     Handles a player exiting the duel.
    ///     Notifies the other player if the duel is cancelled.
    /// </summary>
    /// <param name="event">The duel exited event details.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    private async Task HandleDuelExitedAsync(DuelEvent @event)
    {
        if (_duelManager.TryRemoveParticipant(@event.DuelCode, @event.ConnectionId, out var otherParticipantId) &&
            otherParticipantId != null)
            await _hubContext.Clients.Client(otherParticipantId).DuelCancelled();
    }

    /// <summary>
    ///     Handles a player completing their solve.
    ///     When both players have completed, calculates the result and notifies both players.
    /// </summary>
    /// <param name="event">The solve finished event details.</param>
    /// <returns>A task representing the asynchronous operation.</returns>
    private async Task HandleSolveFinishedAsync(DuelEvent @event)
    {
        if (!_duelManager.TrySetSolveTime(@event.DuelCode, @event.ConnectionId, @event.SolveTime!.Value) ||
            !_duelManager.TryGetDuelResult(@event.DuelCode, out var result))
            return;

        await _hubContext.Clients.Client(result!.HostConnectionId)
            .DuelEnded(result.IsHostWinner, result.IsHostWinner ? result.LoserTime : result.WinnerTime);

        await _hubContext.Clients.Client(result.ChallengerConnectionId)
            .DuelEnded(!result.IsHostWinner, !result.IsHostWinner ? result.LoserTime : result.WinnerTime);

        _duelManager.RemoveDuel(@event.DuelCode);
    }
}