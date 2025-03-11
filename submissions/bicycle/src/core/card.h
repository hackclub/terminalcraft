#pragma once
#include <stdbool.h>

typedef enum Suit : int {
    CLUBS = 1,
    DIAMONDS,
    HEARTS,
    SPADES,
} Suit;

#define MAX_CARD_VALUE 10

typedef enum Rank : int {
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
    KING
} Rank;

typedef struct Card {
    Suit suit;
    int value;
    char face;
} Card;

void deal_cards(Card *deck, int deck_size, int hand_size, int row_size, bool shuffle);
