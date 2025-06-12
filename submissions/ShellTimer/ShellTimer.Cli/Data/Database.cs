using ShellTimer.Cli.Data.Models;
using SQLite;

// ReSharper disable CompareOfFloatsByEqualityOperator

namespace ShellTimer.Cli.Data;

public class Database
{
    private readonly SQLiteConnection _database;

    public Database()
    {
        var folder = Environment.SpecialFolder.ApplicationData;
        var path = Environment.GetFolderPath(folder);
        var dbFolder = Path.Join(path, "ShellTimer");

        Directory.CreateDirectory(dbFolder);

        var dbPath = Path.Join(dbFolder, "ShellTimer.db");
        _database = new SQLiteConnection(dbPath);
        _database.CreateTable<Solve>();
    }

    public void SaveSolve(Solve solve)
    {
        _database.Insert(solve);
    }

    public List<Solve> GetAllSolves(int cubeSize)
    {
        return _database.Table<Solve>()
            .Where(s => s.CubeSize == cubeSize)
            .ToList();
    }

    public List<Solve> GetAllSolves()
    {
        return _database.Table<Solve>().ToList();
    }

    public Solve? GetMostRecentSolve(int cubeSize)
    {
        return _database.Table<Solve>()
            .Where(s => s.CubeSize == cubeSize)
            .OrderByDescending(s => s.DateTime)
            .FirstOrDefault();
    }

    public TimeSpan? GetPersonalBest(int cubeSize)
    {
        var solves = _database.Table<Solve>()
            .Where(s => s.CubeSize == cubeSize && s.Penalty != PenaltyType.DNF)
            .ToList();

        var bestSolve = solves
            .OrderBy(s => s.EffectiveTime)
            .FirstOrDefault();

        return bestSolve?.EffectiveTime;
    }

    public TimeSpan? GetAverageOf(int count, int cubeSize)
    {
        var solves = _database.Table<Solve>()
            .Where(s => s.CubeSize == cubeSize)
            .OrderByDescending(s => s.DateTime)
            .Take(count)
            .ToList();

        if (solves.Count < count)
            return null;

        var times = solves.Select(s =>
                s.Penalty == PenaltyType.DNF ? double.MaxValue :
                s.Penalty == PenaltyType.PlusTwo ? s.TimeInMilliseconds + 2000 :
                s.TimeInMilliseconds)
            .ToList();

        if (count == 5 || count == 12)
        {
            var dnfCount = times.Count(t => t == double.MaxValue);

            if (dnfCount > 1)
                return TimeSpan.MaxValue;

            times = times.OrderBy(t => t).ToList();
            times.RemoveAt(0);
            times.RemoveAt(times.Count - 1);

            return TimeSpan.FromMilliseconds(times.Average());
        }

        if (count == 100)
        {
            var dnfCount = times.Count(t => t == double.MaxValue);

            if (dnfCount > count / 20)
                return TimeSpan.MaxValue;

            times = times.OrderBy(t => t).ToList();

            var toRemove = count / 20;
            times = times.Skip(toRemove).Take(count - 2 * toRemove).ToList();

            if (times.Any(t => t == double.MaxValue))
                return TimeSpan.MaxValue;

            return TimeSpan.FromMilliseconds(times.Average());
        }

        if (times.Any(t => t == double.MaxValue))
            return TimeSpan.MaxValue;

        return TimeSpan.FromMilliseconds(times.Average());
    }

    public Solve? GetSolveById(int id)
    {
        return _database.Table<Solve>()
            .FirstOrDefault(s => s.Id == id);
    }

    public void DeleteSolve(int id)
    {
        _database.Delete<Solve>(id);
    }

    public void UpdateSolvePenalty(int solveId, PenaltyType penalty)
    {
        var solve = _database.Get<Solve>(solveId);
        if (solve != null)
        {
            solve.Penalty = penalty;
            _database.Update(solve);
        }
    }

    public int ClearAllSolves()
    {
        return _database.DeleteAll<Solve>();
    }
}