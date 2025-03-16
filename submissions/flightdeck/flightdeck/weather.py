import requests

def get_weather(api_key, location):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        weather = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        exit(0)
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        exit(0)
        
    if weather:
        try:
            print(f"Current weather in {location}:")
            print(f"Condition: {weather['current']['condition']['text']}")
            print(f"Temperature: {weather['current']['temp_c']}°C")
            print(f"Humidity: {weather['current']['humidity']}%")
            print(f"Wind Speed: {weather['current']['wind_kph']} kph")
        except KeyError:
            print("Error: Could not parse weather data.")