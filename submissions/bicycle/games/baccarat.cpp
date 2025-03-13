#include <print>
#include <vector>
#include "baccarat.h"
#include "../core/card.h"

constexpr uint8_t HAND_SIZE = 3;

uint8_t get_hand_value(const std::vector<Card>& hand, const bool include_third_card) {
    return (hand.at(0).value + hand.at(1).value + (include_third_card ? hand.at(2).value : 0)) % 10;
}

bool should_player_hit(const std::vector<Card>& hand) {
    return get_hand_value(hand, false) < 6;
}

bool should_banker_hit(const std::vector<Card>& banker_hand, const std::vector<Card>& player_hand) {
    const int player_value = player_hand.at(2).value;
    const int banker_value = get_hand_value(banker_hand, false);

    return should_player_hit(player_hand)
        && ((banker_value == 3 && player_value != 8)
            || (banker_value == 4 && player_value > 1 && player_value < 8)
            || (banker_value == 5 && player_value > 3 && player_value < 8)
            || (banker_value == 6 && player_value > 5 && player_value < 8));
}

void play_baccarat(const std::vector<Card>& deck, const int row_size) {
    std::vector<Card> player_hand{};
    std::vector<Card> banker_hand{};
    for (int i = 0; i < HAND_SIZE; ++i) {
        player_hand.push_back(deck.at(i));
        banker_hand.push_back(deck.at(i + HAND_SIZE));
    }

    const bool player_hits = should_player_hit(player_hand);
    const int player_value = get_hand_value(player_hand, player_hits);
    deal_cards(player_hand, player_hits ? HAND_SIZE : HAND_SIZE - 1, row_size, false);
    std::println("Player hand value: {}\n", player_value);

    const bool banker_hits = should_banker_hit(banker_hand, player_hand);
    const int banker_value = get_hand_value(banker_hand, banker_hits);
    deal_cards(banker_hand, banker_hits ? HAND_SIZE : HAND_SIZE - 1, row_size, false);
    std::println("Banker hand value: {}\n", banker_value);

    std::println("{}!", player_value == banker_value ? "Tie" : player_value > banker_value ? "Player wins" : "Banker wins");
}