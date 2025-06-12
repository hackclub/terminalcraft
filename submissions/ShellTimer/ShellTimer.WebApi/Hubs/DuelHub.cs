using System.Threading.Channels;
using Microsoft.AspNetCore.SignalR;
using ShellTimer.WebApi.Models;
using ShellTimer.WebApi.Services;

namespace ShellTimer.WebApi.Hubs;

public class DuelHub : Hub<IDuelHub>
{
    private static readonly Random Random = new();
    private readonly ChannelWriter<DuelEvent> _duelEvents;
    private readonly DuelManager _duelManager;

    public DuelHub(ChannelWriter<DuelEvent> duelEvent, DuelManager duelManager)
    {
        _duelEvents = duelEvent;
        _duelManager = duelManager;
    }

    public async Task CreateDuel(int inspectionTime, int cubeSize, int? scrambleLength)
    {
        await PublishEvent(new DuelEvent
        {
            Type = DuelEventType.DuelCreated,
            ConnectionId = Context.ConnectionId,
            DuelCode = GenerateDuelCode(),
            InspectionTime = inspectionTime,
            CubeSize = cubeSize,
            ScrambleLength = scrambleLength
        });
    }

    public async Task<bool> JoinDuel(string duelCode)
    {
        if (!_duelManager.Duels.ContainsKey(duelCode))
        {
            await Clients.Caller.DuelCancelled();
            return false;
        }

        await PublishEvent(new DuelEvent
        {
            Type = DuelEventType.DuelJoined,
            ConnectionId = Context.ConnectionId,
            DuelCode = duelCode
        });
        return true;
    }

    public Task ReadyForDuel(string duelCode)
    {
        return PublishEvent(new DuelEvent
        {
            Type = DuelEventType.PlayerReady,
            ConnectionId = Context.ConnectionId,
            DuelCode = duelCode
        });
    }

    public Task ExitDuel(string duelCode)
    {
        return PublishEvent(new DuelEvent
        {
            Type = DuelEventType.DuelExited,
            ConnectionId = Context.ConnectionId,
            DuelCode = duelCode
        });
    }

    public Task FinishSolve(string duelCode, int solveTime)
    {
        return PublishEvent(new DuelEvent
        {
            Type = DuelEventType.SolveFinished,
            ConnectionId = Context.ConnectionId,
            DuelCode = duelCode,
            SolveTime = solveTime
        });
    }

    public override async Task OnDisconnectedAsync(Exception? exception)
    {
        var activeDuels = _duelManager.Duels
            .Where(d => d.Value.HostConnectionId == Context.ConnectionId ||
                        d.Value.ChallengedConnectionId == Context.ConnectionId)
            .Select(d => d.Key);

        foreach (var duelCode in activeDuels)
            await PublishEvent(new DuelEvent
            {
                Type = DuelEventType.DuelExited,
                ConnectionId = Context.ConnectionId,
                DuelCode = duelCode
            });

        await base.OnDisconnectedAsync(exception);
    }

    private async Task PublishEvent(DuelEvent @event)
    {
        await _duelEvents.WriteAsync(@event);
    }

    private static string GenerateDuelCode(int length = 6)
    {
        const string chars = "abcdefghijklmnopqrstuvwxyz0123456789";
        return new string(Enumerable.Repeat(chars, length)
            .Select(s => s[Random.Next(s.Length)]).ToArray());
    }
}