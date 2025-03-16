const axios = require("axios");
const readline = require("readline");

const rl = readline.createInterface({
    // cmd boilerplate
    input: process.stdin,
    output: process.stdout
});

async function searchWikipedia(query) {
    // Returns the top 10 search results from a given term
    const url = `https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=${encodeURIComponent(query)}&format=json`;
    try {
        const response = await axios.get(url);
        return response.data.query.search;
    } catch (error) {
        console.error("Error fetching search results:", error);
        return [];
    }
}

async function getFullArticle(title) {
    // Returns the raw text of a given article. (Memory inefficient but no case has had problems so far)
    const url = `https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=true&titles=${encodeURIComponent(title)}&format=json`;
    try {
        const response = await axios.get(url);
        const pages = response.data.query.pages;
        const pageId = Object.keys(pages)[0];
        return pages[pageId]?.extract || "No content available.";
    } catch (error) {
        console.error("Error fetching article content:", error);
        return "Error retrieving article.";
    }
}

rl.question("Enter a search term: ", async (searchTerm) => {
    // Starts up by searching the entered term
    const results = await searchWikipedia(searchTerm);

    if (results.length === 0) {
        console.log("No results found.");
        rl.close();
        return;
    }

    console.log("\nSearch Results:");
    results.forEach((result, index) => {
        console.log(`${index + 1}. ${result.title}`);
    });
    // Selects the article based on a user entered index
    rl.question("\nEnter the number of an article to read: ", async (num) => {
        const index = parseInt(num) - 1;
        if (isNaN(index) || index < 0 || index >= results.length) {
            console.log("Invalid selection.");
            rl.close();
            return;
        }

        // Calls the API to get the text of the article and a list of all the links in the article
        const articleTitle = results[index].title;
        console.log(`\nFetching full article for: ${articleTitle}...\n`);

        const content = await getFullArticle(articleTitle);
        const links = await getWikipediaLinks(articleTitle);

        // Sends the data to be analyzed/printed
        await outputResults(content, links, articleTitle);

        rl.close();
    });
});

async function getWikipediaLinks(title) {
    // Returns every article linked from within a given article
    const url = `https://en.wikipedia.org/w/api.php?action=query&prop=links&pllimit=max&titles=${encodeURIComponent(title)}&format=json`;
    try {
        const response = await axios.get(url);
        const pages = response.data.query.pages;
        const pageId = Object.keys(pages)[0];
        const links = pages[pageId]?.links || [];

        return links.map(link => link.title); // Extract only the link titles
    } catch (error) {
        console.error("Error fetching article links:", error);
        return [];
    }  
}

async function outputResults(text, links, articleTitle) {
    const toSize = (size) => {
        // Converts a nummber of text characters to the file size
        const units = ["B", "KB", "MB", "GB"];
        let unitIndex = 0;
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        return `${size.toFixed(2)} ${units[unitIndex]}`;
    };
    // Attempts to split every word based on spaces, and some punctuation. Some edge cases get through due to the extreme variety of article formatting, but works for the most part
    text = text.replace(/([.,!?;:()])/g, ' $1 ').replace(/\s+/g, ' ').trim();
    var words = text.split(" ");
    words = words.flatMap(word => word.split(/[-#\/+_–­­—­\u00AD]/));
    words = words.filter(word => !/^[.,!?;:()]+$/.test(word));
    words = words.map(word => word.replace(/\[.*?\]/g, ''));

    // Finds the longest word in the article, and checks again to confirm no punctuation is in it.
    words = words.filter(word => word.length > 0);
    var wordCount = words.length;
    var longestWord = words.reduce((a, b) => a.length > b.length ? a : b, "");
    var longestCleanWord = words.reduce((a, b) => (b.indexOf('-') === -1 && b.length > a.length) ? b : a, "");
    var averageWordLength = words.reduce((a, b) => a + b.replace(/[^a-zA-Z]/g, '').length, 0) / wordCount;

    // Finds the most used word not listed in an array of common insubstantial words, or words which hold no meaning themself but exist to carry the sentence grammatically.
    // If this check was not done the most used word would be "the" for almost all articles.
    var filteredWords = words.filter(word => !stopWords.includes(word.toLowerCase()));
    var mostUsedWord = filteredWords.reduce((a, b, i, arr) => {
        const aCount = arr.filter(v => v.toLowerCase() === a.toLowerCase()).length;
        const bCount = arr.filter(v => v.toLowerCase() === b.toLowerCase()).length;
        return aCount >= bCount ? a : b;
    }, "");

    // Checks if the most used word is the same as the article title, which it often is in most articles, and checks for the second most used word if it is.
    const articleTitleLower = articleTitle.toLowerCase();
    if (mostUsedWord.toLowerCase() === articleTitleLower || mostUsedWord.length < 4) {
        const filteredWithoutTitle = filteredWords.filter(word => word.toLowerCase() !== articleTitleLower && word.length >= 4);
        if (filteredWithoutTitle.length > 0) {
            mostUsedWord = filteredWithoutTitle.reduce((a, b, i, arr) => {
                const aCount = arr.filter(v => v.toLowerCase() === a.toLowerCase()).length;
                const bCount = arr.filter(v => v.toLowerCase() === b.toLowerCase()).length;
                return aCount >= bCount ? a : b;
            }, "");
        }
    }
    const mostUsedWordCount = filteredWords.filter(word => word === mostUsedWord).length;

    // Outputs analyzed data.
    console.log("Word Count: " + wordCount);
    console.log("Link Count: " + links.length);
    if (longestWord.length == longestCleanWord.length) {
        console.log("Longest Word: " + longestCleanWord)
    }
    else if (longestCleanWord != longestWord) {
        console.log("Longest Clean Word (No punctuation): " + longestCleanWord)
    }
    console.log("Average Word Length: " + averageWordLength);
    console.log("Size of Text: " + toSize(wordCount + links.join(' ').length));

    console.log("Most Used (Non Title & Substantial) Word: " + mostUsedWord + " (" + mostUsedWordCount + " times)");

    // Lexical density is a percentage of how many of the words in the article are unique words and only appear once.
    const uniqueWords = new Set(words);
    const lexicalDensity = (uniqueWords.size / wordCount) * 100;
    console.log(`Lexical Density: ${lexicalDensity.toFixed(2)}%`);

    // Promts user to scan every article linked to in the root article.
    const result = await new Promise(resolve => rl.question("\nScan all linked articles? (Y/N): ", resolve));
    if (result.toLowerCase() != "y") {
        rl.close();
        return;
    }

    console.log("\Fetching linked articles...\n");

    var analyzedLinks = [];
    var totalWordCount = wordCount;

    for (var i = 0; i < links.length; i++) {
        const content = await getFullArticle(links[i]); // Fetches the raw text
        const words = content.split(" "); // Splits seperate words and punctuation
        totalWordCount += words.length;
        const cleanWords = content.replace(/([.,!?;:()])/g, ' $1 ').replace(/\s+/g, ' ').trim().split(" ").filter(word => !/^[.,!?;:()]+$/.test(word)).map(word => word.replace(/\[.*?\]/g, '')).filter(word => word.length > 0); // AKA the ugliest line of code ever written
        const separatedWords = cleanWords.flatMap(word => word.split(/[-#\/+_–­­—­\u00AD]/));
        const longestSeparatedWord = separatedWords.reduce((a, b) => a.length > b.length ? a : b, ""); // Finds the longest word
        const fetchedLinks = await getWikipediaLinks(links[i]); // Gets the number of links in this article
        analyzedLinks.push({ title: links[i], wordCount: words.length, longestWord: longestSeparatedWord, allWords: separatedWords, links: fetchedLinks});
        // const longestLinkWord = separatedWords.reduce((a, b) => a.length > b.length ? a : b, "");
        let percentage = Math.round((i + 1) / links.length * 1000) / 10; // Outputs a percentage
        process.stdout.write(`\rProgress: ${percentage}% `);
    }

    // Outputs the top five articles in several categories

    const topFiveLongestWords = analyzedLinks
        .sort((a, b) => b.longestWord.length - a.longestWord.length)
        .slice(0, 5)
        .map(link => `${link.title}: ${link.longestWord}`);

    const topFiveWordCounts = analyzedLinks
        .sort((a, b) => b.wordCount - a.wordCount)
        .slice(0, 5)
        .map(link => `${link.title}: ${link.wordCount} words`);

    console.log("\n\nTop 5 Articles by Longest Word:");
    topFiveLongestWords.forEach(item => console.log(item));

    console.log("\nTop 5 Articles by Word Count:");
    topFiveWordCounts.forEach(item => console.log(item));

    console.log("\nTop 5 Articles by Link Count:");
    const topFiveLinkCounts = analyzedLinks
        .sort((a, b) => b.links.length - a.links.length)
        .slice(0, 5)
        .map(link => `${link.title}: ${link.links.length} links`);

    topFiveLinkCounts.forEach(item => console.log(item));

    const topFiveAverageWordLength = analyzedLinks // Calculates more data and then prints it
        .map(link => ({
            title: link.title,
            averageWordLength: link.allWords.reduce((acc, word) => acc + word.length, 0) / link.allWords.length
        }))
        .sort((a, b) => b.averageWordLength - a.averageWordLength)
        .slice(0, 5)
        .map(link => `${link.title}: ${link.averageWordLength.toFixed(2)} characters`);

    console.log("\nTop 5 Articles by Average Word Length:");
    topFiveAverageWordLength.forEach(item => console.log(item));

    const allWords = analyzedLinks.flatMap(link => link.allWords);
    const filteredAllWords = allWords.filter(word => !stopWords.includes(word.toLowerCase()) && word.length > 3);
    const wordFrequency = filteredAllWords.reduce((acc, word) => {
        acc[word] = (acc[word] || 0) + 1;
        return acc;
    }, {});

    const sortedWords = Object.entries(wordFrequency).sort((a, b) => b[1] - a[1]);
    const topFiveWords = sortedWords.slice(0, 5).map(([word, count]) => `${word}: ${count} times`);

    // Prints the top 5 words in EVERY article combined.
    console.log("\nTop 5 Most Used Substantial Words:");
    topFiveWords.forEach(item => console.log(item));

    console.log("\nFile Size Scanned: " + toSize(totalWordCount + links.join(' ').length));

    rl.close();

}

const stopWords = [ // Hopefully every stop word that could possibly be the most used word in an article, plus many more words that are there just in case.
    "a", "an", "the", "and", "or", "but", "if", "then", "because", "since", "so", "thus", "therefore",
    "i", "me", "my", "mine", "myself", "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
    "it", "its", "itself", "we", "us", "our", "ours", "ourselves",
    "they", "them", "their", "theirs", "themselves",
    "this", "that", "these", "those",
    "who", "whom", "whose", "which", "what", "whatever", "whoever", "whomever", "whichever",
    "when", "where", "why", "how",
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having",
    "do", "does", "did", "doing",
    "can", "could", "may", "might", "must", "shall", "should", "will", "would",
    "with", "without", "about", "above", "after", "before", "under", "over",
    "between", "into", "onto", "upon", "to", "of", "for", "from", "in", "on", "at", "by",
    "out", "up", "down", "inside", "outside", "through", "throughout",
    "again", "very", "more", "most", "some", "any", "each", "every", "few", "several", "such", 
    "all", "both", "either", "neither", "one", "two", "first", "next", "last",
    "just", "ever", "never", "always", "sometimes", "almost", "quite", "too", "much", "many",
    "same", "own",
    "there", "here", "other", "another", "because", "since", "hence", "therefore", "thus",
    "and", "but", "or", "nor", "yet", "so", "although", "though", "unless", "while", "whereas", "as"
];
