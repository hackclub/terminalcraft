#include <stdlib.h>
#include "deck.h"

void generate_deck(Card *deck, const int deck_size) {
    Suit suit = CLUBS;
    Rank rank = ACE;

    for (int i = 0; i < deck_size; ++i) {
        deck[i] = (Card){suit, rank > MAX_CARD_VALUE ? MAX_CARD_VALUE : rank, ' '};
        switch (rank) {
            case ACE:
                deck[i].face = 'A';
                break;
            case JACK:
                deck[i].face = 'J';
                break;
            case QUEEN:
                deck[i].face = 'Q';
                break;
            case KING:
                deck[i].face = 'K';
                break;
            default:
                break;
        }

        rank = rank % KING + 1;
        if (rank == ACE)
            suit = suit % SPADES + 1;
    }
}

void shuffle_deck(Card *deck, const int deck_size) {
    for (int i = deck_size - 1; i > 0; --i) {
        const int swap_index = rand() % i;
        const Card swap_card = deck[swap_index];

        deck[swap_index] = deck[i];
        deck[i] = swap_card;
    }
}
