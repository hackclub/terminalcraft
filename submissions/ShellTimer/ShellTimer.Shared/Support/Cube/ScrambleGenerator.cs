namespace ShellTimer.Shared.Support.Cube;

// Based on the official WCA approved scramble generator
public static class ScrambleGenerator
{
    private static readonly Random Random = new();

    private static readonly char[] Faces = ['U', 'D', 'R', 'L', 'F', 'B'];
    private static readonly string[] TurnSuffixes = ["", "'", "2"];

    public static string GenerateScramble(int size, int? length = null)
    {
        if (length == null)
            length = size switch
            {
                2 => 9,
                3 => 20,
                4 => 40,
                5 => 60,
                6 => 80,
                7 => 100,
                _ => size * 20
            }; // WCA standard for different cube sizes

        if (size < 2)
            throw new ArgumentException("Cube size must be at least 2", nameof(size));

        if (length < 0)
            throw new ArgumentException("Scramble length must be non-negative", nameof(length));

        if (size == 2)
            return GenerateScrambleForSize2((int)length);

        var scrambleMoves = new List<string>();
        var lastAxisFace = new[] { -1, -1 };

        for (var i = 0; i < length; i++)
        {
            int axis, face;

            do
            {
                axis = Random.Next(3);
                face = Random.Next(2);
            } while (axis == lastAxisFace[0] && axis == lastAxisFace[1]);

            lastAxisFace[1] = lastAxisFace[0];
            lastAxisFace[0] = axis;

            var faceChar = Faces[axis * 2 + face];

            var isInnerSlice = false;
            var sliceIndex = -1;

            if (size > 3)
            {
                isInnerSlice = Random.Next(3) == 0 && i < length - 1;

                if (isInnerSlice) sliceIndex = Random.Next(1, size / 2); // Inner slice index
            }

            var turnSuffix = TurnSuffixes[Random.Next(TurnSuffixes.Length)];

            string move;
            if (isInnerSlice)
            {
                move = $"{sliceIndex + 1}{faceChar}{turnSuffix}";
            }
            else if (size > 3 && Random.Next(10) < 3)
            {
                var width = Random.Next(2, Math.Min(size, 4));
                move = $"{width}{faceChar}w{turnSuffix}";
            }
            else
            {
                move = $"{faceChar}{turnSuffix}";
            }

            scrambleMoves.Add(move);
        }

        return string.Join(" ", scrambleMoves);
    }

    private static string GenerateScrambleForSize2(int length)
    {
        var scrambleMoves = new List<string>();
        var lastAxis = -1;

        for (var i = 0; i < length; i++)
        {
            int axis;

            do
            {
                axis = Random.Next(3); // 0: UD, 1: RL, 2: FB
            } while (axis == lastAxis);

            lastAxis = axis;

            var faceIdx = axis * 2 + Random.Next(2);
            var faceChar = Faces[faceIdx];
            var turnSuffix = TurnSuffixes[Random.Next(TurnSuffixes.Length)];

            var move = $"{faceChar}{turnSuffix}";

            scrambleMoves.Add(move);
        }

        return string.Join(" ", scrambleMoves);
    }
}