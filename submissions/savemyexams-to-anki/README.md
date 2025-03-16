# SaveMyExams to Anki converter

![Made with VHS](https://vhs.charm.sh/vhs-4gAPvyNwMfUWj415GiK0I6.gif)

A simple tool to convert SaveMyExams flashcards into Anki decks.

## Usage

```sh
savemyexams-to-anki <url to flashcards page> [--reversed]
```

### Options

- `--reversed`: Reverse the term/definition order

## FAQ

### Why is this necessary?

Good question!

### ...really?

Well, Anki is a nicer program for this I guess?

### How does this work?

This tool scrapes the SaveMyExams flashcards page by looking for a `<script type="application/ld+json">` element and converts them into an Anki deck with `genanki-rs`.

---

&copy; 2025 Mahad Kalam.<br>Licensed under the MIT License.
_Please do not perform any actions that may be construed as a violation of copyright._
