namespace ShellTimer.WebApi.Models;

public class DuelEvent
{
    public required DuelEventType Type { get; set; }
    public required string ConnectionId { get; set; }
    public required string DuelCode { get; set; }

    public int? ScrambleLength { get; set; }
    public int? CubeSize { get; set; }
    public int? InspectionTime { get; set; }
    public int? SolveTime { get; set; }
}

public enum DuelEventType
{
    DuelCreated,
    DuelJoined,
    DuelExited,
    PlayerReady,
    SolveFinished
}