using Newtonsoft.Json;

namespace Telescope;

public interface ICosmosObject
{
	[JsonProperty("id")] string Id { get; }
}