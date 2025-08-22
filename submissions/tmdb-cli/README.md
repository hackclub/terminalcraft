# tmdb-cli

`tmdb-cli` is a command-line tool that interacts with the TMDB API. It was originally designed to be useful while implementing API calls in another app or website and to debug responses, etc..

### Dependancies:
- python-dotenv
- requests

If you have an iTerm2 supported terminal, movie covers can be displayed in your console. The following dependancies need to be installed to display images:

- imgcat
- Pillow (required for imgcat)

## Installation

### 1. Clone the repository
```
git clone https://github.com/liamcharger/movie-lookup-cli
cd movie-lookup-cli
```

### 2. Create a venv and activate it
```
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependancies
```
pip install -r requirements.txt
```

If you want to print images to your terminal, you need to install two optional dependancies using the following command:

```
pip install imgcat Pillow
```

And that's it! The app is ready to use.

## Running

### 1. Set environment variables
1. Make sure you have your TMDB API key on hand. You can sign up for a key through your [TMDB account](https://www.themoviedb.org/settings/api).
2. Now we can actually set the API key. There are two ways to do this:
    - Run `python3 main.py config api_key $YOUR_API_KEY`
    - Or if you prefer to do it manually, create a new file named `.env`. Then, add the following line: `API_KEY=$YOUR_API_KEY`.

> [!NOTE]
> Make sure to replace `$YOUR_API_KEY` with the actual key you obtained in step one.

### 2. Run the app!

This app supports five commands:
- `config`: used to set API key and region. [Read more](/docs/config.md)
- `search`: used to find movies or TV shows based on the input. [Read more](/docs/search.md)
- `trending`: this method pulls shows currently trending movies or TV shows. [Read more](/docs/trending.md)
- `details`: this method can be used to fetch additional information about a movie or TV show. [Read more](/docs/details.md)
- `find`: used to fetch movies/TV shows from other sources such as YouTube, IMDB, and more. (Not to be confused with `search`.) [Read more](/docs/find.md)

## Roadmap/To-Do
- [ ] Support actor API
- [ ] Get genre details from ID
- [ ] Add guest authentication to execute actions like submit ratings, etc.
