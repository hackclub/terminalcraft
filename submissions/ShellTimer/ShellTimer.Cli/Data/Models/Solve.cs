using SQLite;

namespace ShellTimer.Cli.Data.Models;

public class Solve
{
    [PrimaryKey] [AutoIncrement] public int Id { get; set; }

    public long TimeInMilliseconds { get; set; }
    public int CubeSize { get; set; }
    public string Scramble { get; set; } = string.Empty;
    public DateTime DateTime { get; set; }
    public PenaltyType Penalty { get; set; } = PenaltyType.None;

    [Ignore]
    public TimeSpan EffectiveTime => Penalty switch
    {
        PenaltyType.PlusTwo => TimeSpan.FromMilliseconds(TimeInMilliseconds + 2000),
        PenaltyType.DNF => TimeSpan.MaxValue,
        _ => TimeSpan.FromMilliseconds(TimeInMilliseconds)
    };
}

public enum PenaltyType
{
    None,
    PlusTwo,
    DNF
}