#include <iostream>
#include <string>
#include <sstream>
#include "card.h"
#include "deck.h"

std::string suit_to_char(const Suit suit) {
    return suit == CLUBS ? "♣" : suit == DIAMONDS ? "♦" : suit == HEARTS ? "♥" : "♠";
}

std::string value_to_string(const Card card) {
    std::stringstream fmt;
    if (card.face == ' ') {
        fmt << (card.value == 10 ? "" : " ") << std::to_string(card.value) << ' ';
    }
    else
        fmt << ' ' << card.face << ' ';
        
    return fmt.str();
}

void deal_cards(std::vector<Card>& deck, uint32_t hand_size, const uint32_t row_size, const bool shuffle) {
    for (int i = 0; i < hand_size; ++i) {
        if (i > deck.size() - 1) {
            if (shuffle)
                shuffle_deck(deck);

            hand_size = hand_size % i;
            i = 0;
        }

        const Card card = deck.at(i);

        if (i % row_size == 0 && i != 0)
            std::cout << "|\n";

        std::cout << "| " << suit_to_char(card.suit) << ' ' << value_to_string(card);
    }
    std::cout << "|\n";
}
