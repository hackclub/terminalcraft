# Terminal Buddy
## Requirements
- The latest version of Python (older versions may work but untested)
## How to run

- Download and extract the files
- Open the terminal/cmd in the directory with the extracted files
- run `pip install -r requirements.txt` to install the required packages

### If you want to have api configuration saved
- Make a config.json file in the directory with the extracted files
- Change it's contents to:
```
{
  "provider": "",
  "model": "",
  "api_key": "",
}
```
- Change the provider field to `openrouter`, `openai` or `ollama`
- Add the APIKey (ignore if it's ollama)
- Choose the model based on the provider's format.

> If you want to stop schema error from happening when using OpenAI or OpenRouter add `"repeatRequest": true` into config.json <br>

> recommended model: `liquid/lfm-3b` on openrouter. It's incredibly cheap and runs well.

- Run the file with `python main.py`
### If you don't want config saved
- Run the file with `python main.py`
## Credits

- OpenWeatherMap API - <https://openweathermap.org/>
