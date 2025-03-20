# Config

This command is used to set environment variables.

```
python3 main.py config SET VALUE
```

- *SET* must be `api_key`, `region`, `img_url`, or `base_url`. 
    - `api_key`: the API key used to make requests to the TMDB API
    - `img_url`: the API URL used to fetch images to display in the terminal (i.e https://api.themoviedb.org/3)
    - `base_url`: the base URL of the TMDB API (i.e https://image.tmdb.org/t/p/w200)
    - `region`: an Alpha-2 country code
- *VALUE* can be any relevant value. Do not wrap strings in quotations as they will be included in the set variable