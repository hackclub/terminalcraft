#include <stdio.h>
#include "card.h"

#include "deck.h"

const char *suit_to_string(const Suit suit) {
    return suit == CLUBS ? "♣" : suit == DIAMONDS ? "♦" : suit == HEARTS ? "♥" : "♠";
}

void value_to_string(char *buf, const Card card) {
    if (card.face == ' ')
        snprintf(buf, sizeof(buf), "%s%d", card.value == 10 ? "" : " ", card.value);
    else
        snprintf(buf, sizeof(buf), " %c", card.face);
}

void deal_cards(Card *deck, const int deck_size, int hand_size, const int row_size, const bool shuffle) {
    for (int i = 0; i < hand_size; ++i) {
        if(i > deck_size - 1) {
            if(shuffle)
                shuffle_deck(deck, deck_size);

            hand_size = hand_size % i;
            i = 0;
        }

        const Card card = deck[i];

        if (i % row_size == 0 && i != 0)
            puts("|");

        char buf[4];
        value_to_string(buf, card);
        printf("| %s %s ",
               suit_to_string(card.suit),
               buf);
    }
    puts("|");
}
