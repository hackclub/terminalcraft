#include <random>
#include <algorithm>
#include "deck.h"

void generate_deck(std::vector<Card>& deck, const uint32_t deck_size) {
    Suit suit = CLUBS;
    Rank rank = ACE;

    for (int i = 0; i < deck_size; ++i) {
        deck.push_back(Card(suit, rank > MAX_CARD_VALUE ? MAX_CARD_VALUE : rank, ' '));
        switch (rank) {
        case ACE:
            deck.at(i).face = 'A';
            break;
        case JACK:
            deck.at(i).face = 'J';
            break;
        case QUEEN:
            deck.at(i).face = 'Q';
            break;
        case KING:
            deck.at(i).face = 'K';
            break;
        default:
            break;
        }

        rank = static_cast<Rank>(rank % KING + 1);
        if (rank == ACE)
            suit = static_cast<Suit>(suit % SPADES + 1);
    }
}

void shuffle_deck(std::vector<Card>& deck) {
    auto rng = std::default_random_engine{};
    std::shuffle(deck.begin(), deck.end(), rng);
}
