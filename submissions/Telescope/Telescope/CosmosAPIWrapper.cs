using System.Net;
using Microsoft.Azure.Cosmos;
using Telescope.Exceptions;

namespace Telescope;

public sealed class CosmosApiWrapper : IDisposable
{
	private CosmosClient? _client;
	private Database? _database;
	private Container? _container;

	private string? _continuationToken;
	public int PageSize;
	private string _query = "";

	public List<List<dynamic>> Pages = [];
	
	public void SetCredentials(string endpoint, string key, int maxRetry = 100, TimeSpan? maxRetryWaitTime = null)
	{
		_client?.Dispose();
		_client = new CosmosClient(endpoint, key)
		{
			ClientOptions =
			{
				AllowBulkExecution = true,
				MaxRetryAttemptsOnRateLimitedRequests = maxRetry,
				MaxRetryWaitTimeOnRateLimitedRequests = maxRetryWaitTime ?? TimeSpan.FromMinutes(1)
			}
		};
	}

	public async Task<bool> VerifyConnection()
	{
		return _client is not null;

		// try
		// {
		// 	FeedIterator<object>? iterator = _client.GetDatabaseQueryIterator<object>();
		// 	await iterator.ReadNextAsync();
		// 	return true;
		// }
		// catch
		// {
		// 	return false;
		// }
	}

	public async Task<List<DatabaseProperties>> ListDatabases()
	{
		if (_client is null)
		{
			throw new InvalidOperationException("You must configure your credentials first");
		}
		
		FeedIterator<DatabaseProperties> resultSetIterator = _client.GetDatabaseQueryIterator<DatabaseProperties>();
		List<DatabaseProperties> databases = [];
		
		while (resultSetIterator.HasMoreResults)
		{
			FeedResponse<DatabaseProperties> response = await resultSetIterator.ReadNextAsync();
			databases.AddRange(response);
		}
		
		return databases;
	}

	public async Task<List<ContainerProperties>> ListContainers()
	{
		if (_database is null)
		{
			throw new InvalidOperationException("No database selected");
		}
		
		FeedIterator<ContainerProperties> resultSetIterator = _database.GetContainerQueryIterator<ContainerProperties>();
		List<ContainerProperties> containers = [];
		
		while (resultSetIterator.HasMoreResults)
		{
			FeedResponse<ContainerProperties> response = await resultSetIterator.ReadNextAsync();
			containers.AddRange(response);
		}
		
		return containers;
	}

	public void SelectDatabase(string databaseId)
	{
		if (_client is null)
		{
			throw new InvalidOperationException("No client created");
		}
		
		_database = _client.GetDatabase(databaseId);
		_container = null;
	}

	public void SelectContainer(string containerId)
	{
		if (_database is null)
		{
			throw new InvalidOperationException("No database selected");
		}

		_container = _database.GetContainer(containerId);
	}

	public void UnselectDatabase()
	{
		_database = null;
		_container = null;
	}

	public async Task CreateItemAsync<T>(T item) where T : ICosmosObject
	{
		if (_container is null)
		{
			throw new InvalidOperationException("No container selected");
		}

		try
		{
			ItemResponse<T> response =
				await _container.CreateItemAsync(item, new PartitionKey(item.Id));

			if (response.StatusCode is HttpStatusCode.Conflict)
			{
				throw new StatusCodeException(HttpStatusCode.Conflict);
			}
		}
		catch (CosmosException ex) when (ex.StatusCode is HttpStatusCode.Conflict)
		{
			throw new StatusCodeException(HttpStatusCode.Conflict);
		}
	}

	public async Task<T> GetItemAsync<T>(Guid id)
	{
		if (_container is null)
		{
			throw new InvalidOperationException("No container selected");
		}

		try
		{
			ItemResponse<T> response =
				await _container.ReadItemAsync<T>(id.ToString(), new PartitionKey(id.ToString()));
			return response.Resource;
		}
		catch (CosmosException e) when (e.StatusCode is HttpStatusCode.NotFound)
		{
			throw new StatusCodeException(HttpStatusCode.NotFound);
		}
	}

	public async Task<bool> GetFirstPageByQueryAsync(string q)
	{
		_query = q;
		Pages = [];
		QueryDefinition query = new(_query);

		List<dynamic> results = [];

		using FeedIterator<dynamic> resultSetIterator = _container.GetItemQueryIterator<dynamic>(
			query,
			requestOptions: new QueryRequestOptions
			{
				MaxItemCount = PageSize
			});

		_continuationToken = null;

		while (resultSetIterator.HasMoreResults)
		{
			// TODO: ORDER BY throws NullReferenceException
			FeedResponse<dynamic> response = await resultSetIterator.ReadNextAsync();

			results.AddRange(response);

			if (response.Count <= 0)
			{
				continue;
			}

			_continuationToken = response.ContinuationToken;
			break;
		}

		Pages.Add(results);
		return _continuationToken is not null;
	}

	public async Task<bool> LoadMore()
	{
		if (_continuationToken is null)
		{
			return false;
		}

		List<dynamic> results = [];

		// Resume query using continuation token
		using FeedIterator<dynamic> resultSetIterator = _container.GetItemQueryIterator<dynamic>(
			_query,
			requestOptions: new QueryRequestOptions
			{
				MaxItemCount = PageSize
			},
			continuationToken: _continuationToken);

		while (resultSetIterator.HasMoreResults)
		{
			FeedResponse<dynamic> response = await resultSetIterator.ReadNextAsync();

			results.AddRange(response);

			if (response.Count <= 0)
			{
				continue;
			}

			_continuationToken = response.ContinuationToken;
			break;
		}

		Pages.Add(results);
		return _continuationToken is not null;
	}
	

	public void Dispose()
	{
		_client?.Dispose();
	}
}