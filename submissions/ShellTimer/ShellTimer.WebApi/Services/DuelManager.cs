using ShellTimer.WebApi.Models;

namespace ShellTimer.WebApi.Services;

/// <summary>
///     Manages duel state, connections, and lifecycle operations.
///     Handles player joining, readiness status, solve times, and cleanup of inactive duels.
/// </summary>
public class DuelManager : IDisposable
{
    private readonly Timer _cleanupTimer;
    private readonly Dictionary<string, DuelState> _duels = new();
    private readonly TimeSpan _inactiveThreshold = TimeSpan.FromHours(1);

    public DuelManager()
    {
        _cleanupTimer = new Timer(CleanupInactiveDuels, null, TimeSpan.Zero, TimeSpan.FromMinutes(10));
    }

    /// <summary>
    ///     Gets a read-only view of all active duels.
    /// </summary>
    public IReadOnlyDictionary<string, DuelState> Duels => _duels;

    public void Dispose()
    {
        _cleanupTimer?.Dispose();
    }


    /// <summary>
    ///     Creates a new duel with the specified parameters.
    /// </summary>
    /// <param name="duelCode">Unique code identifying the duel.</param>
    /// <param name="hostConnectionId">Connection ID of the duel host.</param>
    /// <param name="cubeSize">Size of the cube (e.g., 3 for 3x3x3).</param>
    /// <param name="inspectionTime">Inspection time in seconds.</param>
    /// <param name="scramble">The scramble sequence for the duel.</param>
    /// <returns>True if the duel was created successfully; otherwise, false.</returns>
    public bool TryCreateDuel(string duelCode, string hostConnectionId, int cubeSize, int inspectionTime,
        string scramble)
    {
        if (_duels.ContainsKey(duelCode))
            return false;

        _duels.Add(duelCode, new DuelState
        {
            HostConnectionId = hostConnectionId,
            Scramble = scramble,
            CubeSize = cubeSize,
            InspectionTime = inspectionTime,
            CreatedAt = DateTime.UtcNow
        });
        return true;
    }

    /// <summary>
    ///     Attempts to add a challenger to an existing duel.
    /// </summary>
    /// <param name="duelCode">The duel code to join.</param>
    /// <param name="challengerConnectionId">Connection ID of the joining challenger.</param>
    /// <returns>True if the challenger successfully joined; otherwise, false.</returns>
    public bool TryJoinDuel(string duelCode, string challengerConnectionId)
    {
        if (!TryGetDuel(duelCode, out var duel) || duel.ChallengedConnectionId != null)
            return false;

        duel.ChallengedConnectionId = challengerConnectionId;
        return true;
    }

    /// <summary>
    ///     Marks a player as ready in a duel.
    /// </summary>
    /// <param name="duelCode">The duel code.</param>
    /// <param name="connectionId">Connection ID of the player marking themselves ready.</param>
    /// <returns>True if both players are now ready; otherwise, false.</returns>
    public bool SetPlayerReady(string duelCode, string connectionId)
    {
        if (!TryGetDuel(duelCode, out var duel))
            return false;

        if (duel.HostConnectionId == connectionId)
            duel.HostReady = true;
        else if (duel.ChallengedConnectionId == connectionId)
            duel.ChallengerReady = true;
        else
            return false;

        return duel.AreBothPlayersReady;
    }

    /// <summary>
    ///     Records a player's solve time in a duel.
    /// </summary>
    /// <param name="duelCode">The duel code.</param>
    /// <param name="connectionId">Connection ID of the player.</param>
    /// <param name="solveTime">The solve time in milliseconds.</param>
    /// <returns>True if the solve time was recorded successfully; otherwise, false.</returns>
    public bool TrySetSolveTime(string duelCode, string connectionId, int solveTime)
    {
        if (!TryGetDuel(duelCode, out var duel))
            return false;

        if (duel.HostConnectionId == connectionId)
            duel.HostSolveTime = solveTime;
        else if (duel.ChallengedConnectionId == connectionId)
            duel.ChallengedSolveTime = solveTime;
        else
            return false;

        return true;
    }

    /// <summary>
    ///     Removes a participant from a duel and handles cleanup based on who left.
    /// </summary>
    /// <param name="duelCode">The duel code.</param>
    /// <param name="connectionId">Connection ID of the leaving participant.</param>
    /// <param name="otherParticipantId">Output parameter with the connection ID of the other participant, if any.</param>
    /// <returns>True if the participant was successfully removed; otherwise, false.</returns>
    public bool TryRemoveParticipant(string duelCode, string connectionId, out string? otherParticipantId)
    {
        otherParticipantId = null;
        if (!TryGetDuel(duelCode, out var duel))
            return false;

        if (duel.HostConnectionId == connectionId)
        {
            otherParticipantId = duel.ChallengedConnectionId;
            _duels.Remove(duelCode);
            return true;
        }

        if (duel.ChallengedConnectionId == connectionId)
        {
            otherParticipantId = duel.HostConnectionId;
            duel.ChallengedConnectionId = null;
            duel.ChallengedSolveTime = null;
            duel.ChallengerReady = false;
            return true;
        }

        return false;
    }

    /// <summary>
    ///     Attempts to get the result of a completed duel.
    /// </summary>
    /// <param name="duelCode">The duel code.</param>
    /// <param name="result">Output parameter with the duel result if the duel is complete.</param>
    /// <returns>True if the duel is complete and results are available; otherwise, false.</returns>
    public bool TryGetDuelResult(string duelCode, out DuelResult? result)
    {
        result = null;
        if (!TryGetDuel(duelCode, out var duel) || !duel.AreBothSolvesComplete)
            return false;

        var isHostWinner = duel.HostSolveTime! < duel.ChallengedSolveTime!;
        result = new DuelResult(
            duel.HostConnectionId,
            duel.ChallengedConnectionId!,
            isHostWinner,
            isHostWinner ? duel.HostSolveTime!.Value : duel.ChallengedSolveTime!.Value,
            isHostWinner ? duel.ChallengedSolveTime!.Value : duel.HostSolveTime!.Value
        );
        return true;
    }

    /// <summary>
    ///     Removes a duel from the active duels collection.
    /// </summary>
    /// <param name="duelCode">The duel code to remove.</param>
    public void RemoveDuel(string duelCode)
    {
        _duels.Remove(duelCode);
    }

    /// <summary>
    ///     Attempts to retrieve a duel by its code.
    /// </summary>
    /// <param name="duelCode">The duel code to look up.</param>
    /// <param name="duel">Output parameter that will contain the duel if found.</param>
    /// <returns>True if the duel was found; otherwise, false.</returns>
    public bool TryGetDuel(string duelCode, out DuelState duel)
    {
        return _duels.TryGetValue(duelCode, out duel!);
    }

    /// <summary>
    ///     Cleans up duels that have been inactive for longer than the threshold.
    ///     Removes duels that have been waiting for a challenger for more than an hour.
    /// </summary>
    /// <param name="state">Timer state object (not used).</param>
    private void CleanupInactiveDuels(object? state)
    {
        var now = DateTime.UtcNow;
        var keysToRemove = new List<string>();

        foreach (var (code, duel) in _duels)
            if (duel.ChallengedConnectionId == null &&
                now - duel.CreatedAt > _inactiveThreshold)
                keysToRemove.Add(code);

        foreach (var key in keysToRemove) _duels.Remove(key);
    }
}

public record DuelResult(
    string HostConnectionId,
    string ChallengerConnectionId,
    bool IsHostWinner,
    int WinnerTime,
    int LoserTime);