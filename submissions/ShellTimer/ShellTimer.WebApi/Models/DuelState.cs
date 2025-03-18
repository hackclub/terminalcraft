namespace ShellTimer.WebApi.Models;

public class DuelState
{
    public required string HostConnectionId { get; set; }
    public string? ChallengedConnectionId { get; set; }
    public required string Scramble { get; set; }
    public required int CubeSize { get; set; }
    public required int InspectionTime { get; set; }

    public bool HostReady { get; set; }
    public bool ChallengerReady { get; set; }
    public int? HostSolveTime { get; set; }
    public int? ChallengedSolveTime { get; set; }

    public DateTime CreatedAt { get; set; }

    public bool AreBothPlayersReady => HostReady && ChallengerReady && ChallengedConnectionId != null;

    public bool AreBothSolvesComplete =>
        HostSolveTime.HasValue && ChallengedSolveTime.HasValue && ChallengedConnectionId != null;
}