use std::path::PathBuf;

use clap::Parser;
use color_eyre::{eyre::eyre, Result};
use env_logger::Env;
use genanki_rs::basic_model;
use genanki_rs::Deck;
use genanki_rs::Note;
use reqwest::blocking::Client;
use scraper::{Html, Selector};
use serde::Deserialize;
use url::Url;

/// Convert SaveMyExams flashcards into Anki decks
#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg(value_parser = Url::parse)]
    url: Url,

    #[arg(long)]
    reversed: bool,

    #[arg(short, long)]
    path: Option<PathBuf>,
}

fn main() -> Result<()> {
    color_eyre::install()?;
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();

    let args = Args::parse();
    let set = get_flashcard_set(args.url)?;
    log::info!(
        "Loaded set \"{}\" (contains {} flashcards.)",
        set.name,
        set.flashcards.len()
    );

    let deck_id = gen_id();
    let mut deck = Deck::new(
        deck_id,
        &set.name,
        &format!("Deck for studying {}", set.name),
    );
    log::debug!("Deck ID is {deck_id}.");

    for flashcard in set.flashcards {
        // TODO: I think Anki has its own thing for this
        let note_contents = if args.reversed {
            vec![flashcard.back.as_str(), flashcard.front.as_str()]
        } else {
            vec![flashcard.front.as_str(), flashcard.back.as_str()]
        };
        let note = Note::new(basic_model(), note_contents)?;
        deck.add_note(note);
    }

    let path = args
        .path
        .unwrap_or_else(|| PathBuf::from(format!("{}.apkg", set.name)));

    deck.write_to_file(path.to_str().unwrap())?;
    log::info!("Wrote to {:?}.", path);

    Ok(())
}

#[derive(Deserialize, Debug)]
struct Flashcard {
    front: String,
    back: String,
}

fn gen_id() -> i64 {
    fastrand::i64(0..300_000_000)
}

#[derive(Debug)]
struct FlashcardSet {
    name: String,
    flashcards: Vec<Flashcard>,
}
fn get_flashcard_set(url: Url) -> Result<FlashcardSet> {
    let client = Client::new();
    let html: String = client.get(url).send()?.text()?;
    let document = Html::parse_document(&html);
    let selector = Selector::parse("script[type='application/ld+json']").unwrap();
    let json: serde_json::Value = serde_json::from_str(
        &document
            .select(&selector)
            .next()
            .ok_or(eyre!(
                "no script[type='application/ld+json'] element in document"
            ))?
            .inner_html(),
    )?;

    let set_name = json
        .pointer("/about/name")
        .unwrap()
        .as_str()
        .unwrap()
        .to_string();
    let flashcards: Vec<Flashcard> = json
        .get("hasPart")
        .ok_or(eyre!(
            "flashcards not found in script[type='application/ld+json'] - is your URL valid?"
        ))?
        .clone()
        .as_array()
        .unwrap()
        .iter()
        .map(|value| Flashcard {
            front: value.get("text").unwrap().as_str().unwrap().to_string(),
            back: value
                .pointer("/acceptedAnswer/text")
                .unwrap()
                .as_str()
                .unwrap()
                .to_string(),
        })
        .collect();

    Ok(FlashcardSet {
        name: set_name,
        flashcards,
    })
}
