namespace ShellTimer.WebApi.Hubs;

public interface IDuelHub
{
    Task DuelCreated(string gameCode);

    Task DuelReady(string gameCode, string scramble, int cubeSize, int inspectionTime);

    Task DuelStarted();
    Task DuelEnded(bool isWon, int otherTime);

    Task DuelCancelled();
}