# Terminal Buddy

## How to run
- Make sure you have python installed
- Download the files
- Extract if its zip
- run `pip install -r requirements.txt` on the terminal to install the required libraries
---
### If you want to have api configuration saved
- Make a config.json file
- save this in it:
```
{
  "provider": "",
  "model": "",
  "api_key": "",
}
```
- Update to what you need it to be.

> If you want to stop schema error from happening when using OpenAI or OpenRouter add `"repeatRequest": true` into config.json
> recommended model: `liquid/lfm-3b` on openrouter. It's incredibly cheap and runs well.

- Run the file with `python main.py`
---
### If you don't want config saved
- Just run the file with `python main.py`
---
## Credits

- OpenWeatherMap API - <https://openweathermap.org/>
