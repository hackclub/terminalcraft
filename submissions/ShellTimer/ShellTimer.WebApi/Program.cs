using System.Threading.Channels;
using ShellTimer.WebApi.Hubs;
using ShellTimer.WebApi.Models;
using ShellTimer.WebApi.Services;
using ShellTimer.WebApi.Services.Hosted;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton(Channel.CreateUnbounded<DuelEvent>(new UnboundedChannelOptions
    { SingleReader = true }));

builder.Services.AddSingleton<ChannelReader<DuelEvent>>(svc => svc.GetRequiredService<Channel<DuelEvent>>().Reader);
builder.Services.AddSingleton<ChannelWriter<DuelEvent>>(svc => svc.GetRequiredService<Channel<DuelEvent>>().Writer);

builder.Services.AddSingleton<DuelManager>();

builder.Services.AddHostedService<DuelService>();

builder.Services.AddSignalR();

var app = builder.Build();

app.UseHttpsRedirection();

app.MapHub<DuelHub>("/Duel");

app.Run();