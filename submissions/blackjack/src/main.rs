use rand::prelude::IndexedRandom;
use rand::rng;
use rand::seq::SliceRandom;
use std::io::{self, Write};
use strum::IntoEnumIterator;
use strum_macros::EnumIter;


#[derive(Debug, PartialEq, EnumIter, Clone, Copy)]
enum RANKS {
    ACE = 1,
    TWO,
    THREE,
    FOUR,
    FIVE,
    SIX,
    SEVEN,
    EIGHT,
    NINE,
    TEN,
    JACK,
    QUEEN,
    KING,
}

#[derive(Debug, EnumIter)]
enum SUITS {
    SPADE,
    HEART,
    DIAMOND,
    CLUB,
}

fn create_deck() -> Vec<(RANKS, SUITS)> {
    let mut deck: Vec<(RANKS, SUITS)> = Vec::new();
    for rank in RANKS::iter() {
        for suit in SUITS::iter() {
            deck.push((rank, suit))
        }
    }
    deck.shuffle(&mut rng());
    deck
}

fn hand_value(hand: &[(RANKS, SUITS)]) -> u8 {
    let mut score = 0;
    let mut ace_count = hand.iter().filter(|card| card.0 == RANKS::ACE).count();

    for &(rank, _) in hand {
        let value = rank as u8;
        match value {
            2..=10 => score += value,
            1 => score += 11,
            _ => score += 10,
        }
    }

    while score > 21 && ace_count > 0 {
        score -= 10;
        ace_count -= 1;
    }

    score
}

fn print_hand(name: &str, hand: &[(RANKS, SUITS)], hidden: bool) {
    if hidden && hand.len() > 1 {
        let (_, suit) = &hand[1];
        println!(
            "🃏 {}'s Hand: [🂠 Hidden], {:?} of {:?}",
            name, hand[1].0, suit
        );
    } else {
        let cards: Vec<String> = hand
            .iter()
            .map(|(rank, suit)| format!("{:?} of {:?}", rank, suit))
            .collect();
        let hand_str = cards.join(" 🎴 ");
        println!(
            "🃏 {}'s Hand: {} 🎯 (Total: {})",
            name,
            hand_str,
            hand_value(hand)
        );
    }
}

fn get_input(prompt: &str) -> String {
    print!("{}", prompt);
    io::stdout().flush().unwrap();
    let mut buf = String::new();
    io::stdin().read_line(&mut buf).unwrap();
    buf.trim().to_uppercase()
}

fn play_blackjack() {
    println!("♠️♥️ Welcome to Blackjack! ♦️♣️\n");

    let mut deck = create_deck();
    let mut player_hand = vec![deck.pop().unwrap(), deck.pop().unwrap()];
    let mut dealer_hand = vec![deck.pop().unwrap(), deck.pop().unwrap()];

    print_hand("Dealer", &dealer_hand, true);
    print_hand("Player", &player_hand, false);

    loop {
        let choice = get_input("👉 Do you want to Hit (H) or Stand (S)? ");
        if choice == "H" {
            println!("🃏 You chose to hit!");
            player_hand.push(deck.pop().unwrap());
            print_hand("Player", &player_hand, false);
            if hand_value(&player_hand) > 21 {
                println!("💥 Player busts! Dealer wins. 😞");
                return;
            }
        } else if choice == "S" {
            println!("🛑 You chose to stand.");
            break;
        } else {
            println!("❌ Invalid choice. Type H or S.");
        }
    }

    println!("\n🔄 Dealer's turn...");
    print_hand("Dealer", &dealer_hand, false);
    while hand_value(&dealer_hand) < 17 {
        println!("🎴 Dealer hits!");
        dealer_hand.push(deck.pop().unwrap());
        print_hand("Dealer", &dealer_hand, false);
    }

    let player_score = hand_value(&player_hand);
    let dealer_score = hand_value(&dealer_hand);

    println!("\n🎉 Final Results:");
    println!("🧑 Player: {} points", player_score);
    println!("🧑‍💼 Dealer: {} points", dealer_score);

    println!();
    if dealer_score > 21 {
        println!("💥 Dealer busts! 🎉 Player wins!");
    } else if player_score > dealer_score {
        println!("🏆 Player wins!");
    } else if player_score < dealer_score {
        println!("😞 Dealer wins!");
    } else {
        println!("🤝 It's a tie!");
    }
}

fn play_jackpot() {
    let symbols = ["🍒", "🍋", "💎", "🔔", "⭐", "🍇"];
    let mut rng = rand::rng();

    let mut wins = 0;
    let mut losses = 0;

    println!("🎰 Welcome to Rusty Jackpot! 🎰");
    println!("Match all 3 symbols to win!\n");

    loop {
        print!("Press Enter to spin (or type 'q' to quit): ");
        io::stdout().flush().unwrap();

        let mut input = String::new();
        io::stdin().read_line(&mut input).unwrap();
        let trimmed = input.trim();

        if trimmed.eq_ignore_ascii_case("q") {
            break;
        }

        // Spin the reels
        let slot: Vec<String> = (0..3)
            .map(|_| symbols.choose(&mut rng).unwrap().to_string())
            .collect();

        println!("🎲 Result: {} | {} | {}", slot[0], slot[1], slot[2]);

        if slot[0] == slot[1] && slot[1] == slot[2] {
            println!("🎉 Jackpot! You win!\n");
            wins += 1;
        } else {
            println!("💨 Sorry, try again.\n");
            losses += 1;
        }
    }

    // Final stats
    println!("\n🧾 Game Over");
    println!("✅ Wins: {}", wins);
    println!("❌ Losses: {}", losses);
    println!(
        "🧠 Win rate: {:.2}%",
        if wins + losses > 0 {
            100.0 * wins as f32 / (wins + losses) as f32
        } else {
            0.0
        }
    );
}

fn main() {
    println!("🎮 Welcome to the Rusty Casino! 🦀");
    println!("==================================");
    println!("🎲 Games Available:");
    println!("1️⃣  Blackjack");
    println!("2️⃣  Jackpot Slot Machine");
    println!("🚪  Type 'q' to quit anytime.");
    println!("----------------------------------");

    loop {
        let choice = get_input("\n🔢 Enter your choice (1 or 2): ");

        if choice == "1" {
            println!("\n🃏 Starting Blackjack...\n");
            play_blackjack();
        } else if choice == "2" {
            println!("\n🎰 Spinning the Jackpot...\n");
            play_jackpot();
        } else if choice == "q" || choice == "Q" {
            println!("\n👋 Thanks for playing! Goodbye!\n");
            break;
        } else {
            println!("❌ Invalid choice. Please enter 1, 2, or 'q' to quit.");
        }
    }
}
