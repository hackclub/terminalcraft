#include <stdlib.h>
#include <stdio.h>
#include <cargs.h>
#include "core/deck.h"
#include "core/clock.h"
#include "games/baccarat.h"

#define CARDS_PER_DECK 52
int row_size = 5, hand_size = 1, deck_size = CARDS_PER_DECK;
long int seed = -1;
bool shuffle = true, baccarat = false;

struct cag_option options[] = {
    {
        .identifier = 'r',
        .access_letters = "r",
        .access_name = "row-size",
        .value_name = "SIZE",
        .description = "Maximum cards displayed in one row"
    },
    {
        .identifier = 'c',
        .access_letters = "c",
        .access_name = "cards",
        .value_name = "AMOUNT",
        .description = "Number of cards dealt"
    },
    {
        .identifier = 'd',
        .access_letters = "d",
        .access_name = "decks",
        .value_name = "NUMBER",
        .description = "Number of decks in the shoe"
    },
    {
        .identifier = 's',
        .access_letters = "s",
        .access_name = "seed",
        .value_name = "SEED",
        .description = "RNG seed for shuffling"
    },
    {
        .identifier = 'b',
        .access_letters = "b",
        .access_name = "baccarat",
        .value_name = NULL,
        .description = "Play a game of baccarat"
    },
    {
        .identifier = 'n',
        .access_letters = "n",
        .access_name = "no-shuffle",
        .value_name = NULL,
        .description = "Deal cards without shuffling"
    },
    {
        .identifier = 'h',
        .access_letters = "h",
        .access_name = "help",
        .description = "Displays the help message"
    },
};

void print_usage(FILE *destination) {
    puts("Usage: bicycle [OPTION]...");
    cag_option_print(options, CAG_ARRAY_SIZE(options), destination);
}

long int argtoi(const cag_option_context *context) {
    char *endptr;
    const char *option_value = cag_option_get_value(context);
    const long int value = strtol(option_value, &endptr, 10);

    if (endptr == option_value || *endptr != '\0' || value <= 0) {
        print_usage(stderr);
        printf("Argument for option '%c' must be a number greater than 0.\n", cag_option_get_identifier(context));
        exit(EXIT_FAILURE);
    }

    return value;
}

void process_arguments(int argc, char *argv[]) {
    cag_option_context context;
    cag_option_init(&context, options, CAG_ARRAY_SIZE(options), argc, argv);
    while (cag_option_fetch(&context)) {
        switch (cag_option_get_identifier(&context)) {
            case 'r':
                row_size = argtoi(&context);
                break;
            case 'c':
                hand_size = argtoi(&context);
                break;
            case 'd':
                deck_size = argtoi(&context);
                break;
            case 's':
                seed = argtoi(&context);
                break;
            case 'b':
                baccarat = true;
                break;
            case 'n':
                shuffle = false;
                break;
            case 'h':
                print_usage(stdout);
                exit(EXIT_SUCCESS);
            case '?':
                print_usage(stderr);
                cag_option_print_error(&context, stderr);
                exit(EXIT_FAILURE);
        }
    }

    if (seed == -1)
        seed = get_time_in_usec();
}

int main(int argc, char *argv[]) {
    process_arguments(argc, argv);

    Card *deck = malloc(deck_size * sizeof(Card));
    generate_deck(deck, deck_size);
    if (shuffle) {
        srand(seed);
        shuffle_deck(deck, deck_size);
    }

    if (baccarat)
        play_baccarat(deck, row_size);
    else
        deal_cards(deck, deck_size, hand_size, row_size, shuffle);

    free(deck);
    return 0;
}