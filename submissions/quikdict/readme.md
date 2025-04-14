# quikdict

A simple go program to quickly look up (english) words and get IPA, meanings and sometimes examples, synonyms and antonyms.  
The application can also translate a word to a different language using Google Translate.  
It does require an online connection (no offline functionality) but it doesn't require any key/login/data to use.

## Usage
You can find a compiled binary in the [releases](https://github.com/spacefall/quikdict/releases).  
You can also compile it yourself by running `go build` after cloning the repo with `git clone https://github.com/spacefall/quikdict.git`.  
You could also use a server running the application (see below) and a browser or curl to get colored output.

After obtaining a binary, you can get the meaning and examples by running:
```bash
./quickdict <word>
```

If you want synonyms and antonyms, you can run:
```bash
./quickdict -th <word>
```

If instead you want to translate a word, run:
```bash
./quickdict -tr <lc> <word>
```
where `<lc>` is the language code of the language you want to translate to, for example: `en` for English, `it` for Italian, `es` for Spanish, `fr` for French, `de` for German.
The source language is obtained automatically by Google Translate.

## Server
You can also run the application as a server by running:
```bash
./quickdict -s
```
An active deployment can be found [here](https://quikdict.onrender.com/).

This will start a server on `localhost:8246` that you can query with a browser or curl.
Using the server, you won't get colored output unless you use curl, but the output will be the same as the terminal app. The only thing that changes is the query parameters.

You can get the meaning and examples by adding the word to the URL, for example, using `hello`:
```
http://localhost:8246/hello
```

If you want synonyms and antonyms, you can add `?th`:
```
http://localhost:8246/hello?th
```

If instead you want to translate a word:
```
http://localhost:8246/hello?tr=it
```

where `it` is just an example and represents the language code of the language you want to translate to, for example: `en` for English, `it` for Italian, `es` for Spanish, `fr` for French, `de` for German.
The source language is obtained automatically by Google Translate.

## Sources
The dictionary/thesaurus data is obtained from [DictionaryAPI](https://dictionaryapi.dev/), which obtains its data from [Wikitionary](https://en.wiktionary.org/wiki/Wiktionary:Main_Page).  
The translation data is obtained from Google Translate.
