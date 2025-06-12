// See https://aka.ms/new-console-template for more information

using ShellTimer.Cli.Commands;
using Spectre.Console.Cli;

var app = new CommandApp();

app.Configure(config =>
{
    config.AddCommand<TimerCommand>("timer")
        .WithDescription("Start timing solves");

    config.AddCommand<ScrambleCommand>("scramble")
        .WithDescription("Generate scrambles for a specific cube size");

    config.AddBranch("solves", solves =>
    {
        solves.SetDescription("Manage solve records");

        solves.AddCommand<ListCommand>("list")
            .WithDescription("List all solve records");

        solves.AddCommand<DeleteCommand>("delete")
            .WithDescription("Delete a solve record by its ID");

        solves.AddCommand<ClearCommand>("clear")
            .WithDescription("Clear all solve records from the database");
    });

    config.AddCommand<StatsCommand>("stats")
        .WithDescription("Show statistics for a specific cube size");

    config.AddCommand<DuelCommand>("duel")
        .WithDescription("Duel an other ShellTimer user in real-time");

    config.AddCommand<ConfigCommand>("config")
        .WithDescription("Configure ShellTimer with application wide settings");
});

return app.Run(args);