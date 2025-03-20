# Search

This command is used to search for movies or TV shows that match the provided query.

```
python3 main.py search TYPE QUERY --flags
```

- *TYPE* must either be `movie` or `tv`
- *QUERY* should be a string value

This command supports three flags, all of which are optional:
- **-p, --page** `integer`: The index of the page to return<sup>1</sup>
- **-c, --count** `integer`: The number of results to return<sup>2</sup>
- **--json**: Creates a `search.json` file in the project directory containing the API response

<sup>1</sup> *A page is created for every 10 results*
<br>
<sup>2</sup> *A value 10 or above will not affect the result*