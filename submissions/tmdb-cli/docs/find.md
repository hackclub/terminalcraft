# Find

This command is used to fetch a movie/TV show using its ID from another provider.

```
python3 main.py find ID --flags
```

- *ID* should be the ID of the media that corresponds to platform you specify

This command ***requires*** one flag. The flag should relate to the platform your media ID is from:
- --imdb
- --facebook
- --instagram
- --tvdb
- --tiktok
- --wikidata
- --youtube

In addition to the commands above, there are three more one available ***optional*** flags:
- **-p, --page** `integer`: The index of the page to return<sup>1</sup>
- **-c, --count** `integer`: The number of results to return<sup>2</sup>
- **--json**: Creates a `find.json` file in the project directory containing the API response

<sup>1</sup> *A page is created for every 10 results*
<br>
<sup>2</sup> *A value 10 or above will not affect the result*
