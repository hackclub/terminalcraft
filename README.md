# HackClubWiki
 A Wikipedia data analyzer, built using NodeJS and Axios.


# How to run
 * Download the source and extract
 * Open CMD and cd to the project directory
 * Run `node main.js`
 * If you get an error about not having Axios, run `npm install axios` and run main again
 * When promted, type in the name of a Wikipedia article, press enter, and enter the number for the desired article
 * If you want to scan linked articles, enter Y when prompted (This may take a while)

# Why make this?
 I've been thinking of making a larger Wikipedia project, and wanted to start small while learning new things about Wikipedia in the process.

# Known errors
 Every article is formatted *slightly* differently, and some cases may cause some blips in the analysis.

# API usage
 Fetching the entire text of potentially several hundred articles seems like it would take a lot of data up, but the average scan requests size than a single visit to a single article. The API only gets text, and does not get formatting, styling, images, references, and other assets.
