#include <stdio.h>
#include <stdbool.h>
#include "baccarat.h"
#include "../core/card.h"

#define HAND_SIZE 3

int get_hand_value(const Card *hand, const bool include_third_card) {
    return (hand[0].value + hand[1].value + (include_third_card ? hand[2].value : 0)) % 10;
}

bool should_player_hit(const Card *hand) {
    return get_hand_value(hand, false) < 6;
}

bool should_banker_hit(const Card *banker_hand, const Card *player_hand) {
    const int player_value = player_hand[2].value;
    const int banker_value = get_hand_value(banker_hand, false);

    return should_player_hit(player_hand)
    && ((banker_value == 3 && player_value != 8)
        || (banker_value == 4 && player_value > 1 && player_value < 8)
        || (banker_value == 5 && player_value > 3 && player_value < 8)
        || (banker_value == 6 && player_value > 5 && player_value < 8));
}

void play_baccarat(const Card *deck, const int row_size) {
    Card player_hand[HAND_SIZE];
    Card banker_hand[HAND_SIZE];
    for (int i = 0; i < HAND_SIZE; ++i) {
        player_hand[i] = deck[i];
        banker_hand[i] = deck[i + HAND_SIZE];
    }

    const bool player_hits = should_player_hit(player_hand);
    const int player_value = get_hand_value(player_hand, player_hits);
    deal_cards(player_hand, HAND_SIZE, player_hits ? HAND_SIZE : HAND_SIZE - 1, row_size, false);
    printf("Player hand value: %d\n\n", player_value);

    const bool banker_hits = should_banker_hit(banker_hand, player_hand);
    const int banker_value = get_hand_value(banker_hand, banker_hits);
    deal_cards(banker_hand, HAND_SIZE, banker_hits ? HAND_SIZE : HAND_SIZE - 1, row_size, false);
    printf("Banker hand value: %d\n\n", banker_value);

    printf("%s!\n", player_value == banker_value ? "Tie" : player_value > banker_value ? "Player wins" : "Banker wins");
}