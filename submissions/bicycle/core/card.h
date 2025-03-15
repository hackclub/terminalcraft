#pragma once
#include <vector>
#include <cstdint>

typedef enum Suit : uint8_t {
    CLUBS = 1,
    DIAMONDS,
    HEARTS,
    SPADES,
} Suit;

constexpr uint8_t MAX_CARD_VALUE = 10;

typedef enum Rank : uint8_t {
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
    uint8_t value;
    char face;

    Card(Suit s, uint8_t v, char f) : suit(s), value(v), face(f) {}
} Card;

void deal_cards(std::vector<Card>& deck, uint32_t hand_size, uint32_t row_size, bool shuffle);
