# LLM API

The API powering the Sprig LLM functionality.

# Running the project locally

In order to run the project, you will need the following already setup.

- Python 
- Postgres

After cloning the repository and `cd llm-api`, do the following

Install the dependencies with 
```shell
pip install -r requirements.txt
```


Copy the `.env.example` into a `.env` 
```shell
cp .env.example .env
```

In a new terminal window, start the postgresql server and create a new user with

```sql
CREATE USER <username> WITH ENCRYPTED PASSWORD <password>;
```
and create a database named `sprigllmtest` with
```shell
CREATE DATABASE sprigllmtest;
```
In the `.env` replace the value of `PG_DATABASE_URL` with your connection string of the form `postgresql://<username>:<password>@localhost:5432/sprigllmtest`

Start the development server with 
```shell
uvicorn main:app --reload
```

If you don't get any errors, the app should be running properly.

## Making API requests

An API requests looks like
```
{
    message: ,
    session_id: ,
    email: ,
}
```

The API will return a reponse containing the raw output from the model and a property called `codes` containing the list of code blocks the API extracted from the model response.

By default, the API keeps a history of the requests sent to it so you don't have to worry about sending a list of the previous messages.

## CORS 
By default, `localhost:3000` is an authorized origin in teh LLM API

If you want to allow a URL authorized, add the URL to `allow_origins` in the CORS middleware
```diff python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sprig.hackclub.com",
        "http://localhost:3000",
        "https://sprig-git-sprig-ai.hackclub.dev",
        "https://sprig.hackclub.com",
+       "https://your-new-url.com"
    ],
```

If you've got questions or would like to learn more, please visit [#hq-engineering](https://hackclub.slack.com/archives/C05SVRTCDGV) on Hack Club's slack.