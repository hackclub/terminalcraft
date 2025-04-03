using System.Net;

namespace Telescope.Exceptions;

public class StatusCodeException(HttpStatusCode statusCode) : Exception
{
	public HttpStatusCode StatusCode { get; } = statusCode;
}