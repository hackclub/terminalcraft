# Details

This command is used to get details for a movie/TV show by its TMDB ID.

```
python3 main.py details TYPE ID --flags
```

- *TYPE* must either be `movie` or `tv`
- *ID* is the TMDB ID of the media.

This command supports one optional flag:
- **--json**: Creates a `details.json` file in the project directory containing the API response
