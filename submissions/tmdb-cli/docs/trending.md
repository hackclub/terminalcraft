# Trending

This command is used to get the currently trending movies or TV shows in your region.

```
python3 main.py trending TYPE --flags
```

- *TYPE* must be either `movie` or `tv`.

This command supports three flags, all of which are optional:
- **-p, --page** `integer`: The index of the page to return<sup>1</sup>
- **-c, --count** `integer`: The number of results to return<sup>2</sup>
- **--json**: Creates a `trending.json` file in the project directory containing the API response

<sup>1</sup> *A page is created for every 10 results*
<br>
<sup>2</sup> *A value 10 or above will not affect the result*
