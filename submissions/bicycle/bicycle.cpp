#include <print>
#include <vector>
#include "core/card.h"
#include "core/deck.h"
#include "games/baccarat.h"
#include "cargs/include/cargs.h"

constexpr uint8_t CARDS_PER_DECK{ 52 };
uint32_t row_size{ 5 }, hand_size{ 1 }, deck_size{ CARDS_PER_DECK };
bool shuffle{ true }, baccarat{ false };

struct cag_option options[]{
    {
        'r',
        "r",
        "row-size",
        "SIZE",
        "Maximum cards displayed in one row"
    },
    {
        'c',
        "c",
        "cards",
        "AMOUNT",
        "Number of cards dealt"
    },
    {
        'd',
        "d",
        "decks",
        "NUMBER",
        "Number of decks in the shoe"
    },
    {
        'b',
        "b",
        "baccarat",
        nullptr,
        "Play a game of baccarat"
    },
    {
        'n',
        "n",
        "no-shuffle",
        nullptr,
        "Deal cards without shuffling"
    },
    {
        'h',
        "h",
        "help",
        nullptr,
        "Displays the help message"
    },
};

void print_usage(FILE* destination) {
    std::println("Usage: bicycle [OPTION]...");
    cag_option_print(options, CAG_vector_SIZE(options), destination);
}

static uint32_t argtoi(const cag_option_context* context) {
    char* endptr{};
    const char* option_value{ cag_option_get_value(context) };
    const int value{ strtol(option_value, &endptr, 10) };

    if (endptr == option_value || *endptr != '\0' || value <= 0) {
        print_usage(stderr);
        std::println("Argument for option '%c' must be a number greater than 0.\n", cag_option_get_identifier(context));
        exit(EXIT_FAILURE);
    }

    return value;
}

void process_arguments(int argc, char* argv[]) {
    cag_option_context context;
    cag_option_init(&context, options, CAG_vector_SIZE(options), argc, argv);
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
}

int main(int argc, char* argv[]) {
    process_arguments(argc, argv);

    std::vector<Card> deck{};
    generate_deck(deck, deck_size);
    if (shuffle) {
        shuffle_deck(deck);
    }

    if (baccarat)
        play_baccarat(deck, row_size);
    else
        deal_cards(deck, hand_size, row_size, shuffle);

    return 0;
}