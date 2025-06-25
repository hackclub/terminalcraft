#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <stdbool.h>

#define MAX_SIZE 10
#define MIN_SIZE 3
#define EMPTY ' '

char **board;
char PLAYER, PLAYER2;
int boardSize = 3;
int is_multiplayer = 0;
int move_history[MAX_SIZE * MAX_SIZE][2], move_count = 0;
char player1Name[50], player2Name[50];

void resetBoard();
void printBoard();
int getFreeSpaces();
void playerMove(int player);
void computerMove();
char checkWinner();
void printWinner(char);
void character();
void menu();
void selectMode();
void setBoardSize();
void undoMove();
void replayGame();
void updateLeaderboard(const char *playerName);
void refreshLeaderboard();
void displayLeaderboard();

int main() {
    char response;
    refreshLeaderboard();
    do {
        menu();
        selectMode();
        setBoardSize();
        printf("Enter Player 1's name: ");
        scanf("%s", player1Name);
        if (is_multiplayer == 2) {
            printf("Enter Player 2's name: ");
            scanf("%s", player2Name);
        } else {
            strcpy(player2Name, "Computer");
        }
        character();
        char winner = ' ';
        resetBoard();
        move_count = 0;

        while (winner == ' ' && getFreeSpaces() != 0) {
            printBoard();
            if (is_multiplayer == 1) {
                playerMove(1);
                winner = checkWinner();
                if (winner != ' ' || getFreeSpaces() == 0) break;
                computerMove();
            } else if (is_multiplayer == 2) {
                playerMove(1);
                winner = checkWinner();
                if (winner != ' ' || getFreeSpaces() == 0) break;
                playerMove(2);
            }
            winner = checkWinner();
        }
        printBoard();
        printWinner(winner);
        printf("\nWould you like to replay the game? (Y/N): ");
        scanf(" %c", &response);
        response = toupper(response);
        if (response == 'Y') replayGame();
        printf("\nWould you like to play again? (Y/N): ");
        scanf(" %c", &response);
        response = toupper(response);
    } while (response == 'Y');
    printf("Thanks for playing!\n");
    return 0;
}

void resetBoard() {
    board = (char **)malloc(boardSize * sizeof(char *));
    for (int i = 0; i < boardSize; i++) {
        board[i] = (char *)malloc(boardSize * sizeof(char));
        for (int j = 0; j < boardSize; j++) {
            board[i][j] = EMPTY;
        }
    }
}

void printBoard() {
    printf("\n");
    for (int i = 0; i < boardSize; i++) {
        for (int j = 0; j < boardSize; j++) {
            printf(" %c ", board[i][j]);
            if (j < boardSize - 1) printf("|");
        }
        printf("\n");
        if (i < boardSize - 1) {
            for (int j = 0; j < boardSize; j++) {
                printf("---");
                if (j < boardSize - 1) printf("+");
            }
            printf("\n");
        }
    }
    printf("\n");
}

int getFreeSpaces() {
    int freeSpaces = 0;
    for (int i = 0; i < boardSize; i++) {
        for (int j = 0; j < boardSize; j++) {
            if (board[i][j] == EMPTY) {
                freeSpaces++;
            }
        }
    }
    return freeSpaces;
}

void playerMove(int player) {
    int x, y;
    char symbol = (player == 1) ? PLAYER : PLAYER2;
    char *playerName = (player == 1) ? player1Name : player2Name;
    do {
        printf("%s (%c), enter row #(1-%d): ", playerName, symbol, boardSize);
        scanf("%d", &x);
        x--;
        printf("Enter column #(1-%d): ", boardSize);
        scanf("%d", &y);
        y--;
        if (x < 0 || x >= boardSize || y < 0 || y >= boardSize || board[x][y] != EMPTY) {
            printf("Invalid move, try again.\n");
        } else {
            board[x][y] = symbol;
            move_history[move_count][0] = x;
            move_history[move_count][1] = y;
            move_count++;
            break;
        }
    } while (1);
}

void computerMove() {
    int x, y;
    srand(time(0));
    do {
        x = rand() % boardSize;
        y = rand() % boardSize;
    } while (board[x][y] != EMPTY);
    board[x][y] = PLAYER2;
    printf("Computer chose row %d and column %d\n", x + 1, y + 1);
}

char checkWinner() {
    for (int i = 0; i < boardSize; i++) {
        bool rowWin = true, colWin = true;
        for (int j = 1; j < boardSize; j++) {
            if (board[i][j] != board[i][0] || board[i][0] == EMPTY) rowWin = false;
            if (board[j][i] != board[0][i] || board[0][i] == EMPTY) colWin = false;
        }
        if (rowWin) return board[i][0];
        if (colWin) return board[0][i];
    }
    bool diag1Win = true, diag2Win = true;
    for (int i = 1; i < boardSize; i++) {
        if (board[i][i] != board[0][0] || board[0][0] == EMPTY) diag1Win = false;
        if (board[i][boardSize - i - 1] != board[0][boardSize - 1] || board[0][boardSize - 1] == EMPTY) diag2Win = false;
    }
    if (diag1Win) return board[0][0];
    if (diag2Win) return board[0][boardSize - 1];
    return ' ';
}

void printWinner(char winner) {
    if (winner == PLAYER) {
        printf("%s WINS!\n", player1Name);
        updateLeaderboard(player1Name);
    } else if (winner == PLAYER2) {
        printf("%s WINS!\n", player2Name);
        updateLeaderboard(player2Name);
    } else {
        printf("IT'S A TIE!\n");
    }
}

void menu() {
    printf("WELCOME TO TIC-TAC-TOE\n");
    displayLeaderboard();
}

void selectMode() {
    printf("Select Mode: \n1. Single Player\n2. Local Multiplayer\nEnter choice: ");
    scanf("%d", &is_multiplayer);
}

void character() {
    printf("%s, choose your symbol: ", player1Name);
    scanf(" %c", &PLAYER);
    if (is_multiplayer == 2) {
        printf("%s, choose your symbol: ", player2Name);
        scanf(" %c", &PLAYER2);
    } else {
        PLAYER2 = 'O';
    }
    if (PLAYER == PLAYER2) {
        printf("Symbols cannot be the same. Defaulting to X and O.\n");
        PLAYER = 'X';
        PLAYER2 = 'O';
    }
}

void setBoardSize() {
    printf("Enter board size (3-10): ");
    scanf("%d", &boardSize);
    if (boardSize < MIN_SIZE || boardSize > MAX_SIZE) {
        printf("Invalid size. Defaulting to 3x3.\n");
        boardSize = 3;
    }
}

void undoMove() {
    if (move_count > 0) {
        move_count--;
        int x = move_history[move_count][0];
        int y = move_history[move_count][1];
        board[x][y] = EMPTY;
        printf("Last move undone.\n");
    } else {
        printf("No moves to undo.\n");
    }
}

void replayGame() {
    printf("Replaying the game...\n");
    resetBoard();
    for (int i = 0; i < move_count; i++) {
        int x = move_history[i][0];
        int y = move_history[i][1];
        board[x][y] = (i % 2 == 0) ? PLAYER : PLAYER2;
        printBoard();
    }
}

void updateLeaderboard(const char *playerName) {
    FILE *file = fopen("leaderboard.txt", "a");
    if (file == NULL) {
        return;
    }
    fprintf(file, "%s\n", playerName);
    fclose(file);
}

void refreshLeaderboard() {
    FILE *file = fopen("leaderboard.txt", "w");
    if (file != NULL) {
        fclose(file);
    }
}

void displayLeaderboard() {
    FILE *file = fopen("leaderboard.txt", "r");
    if (file == NULL) {
        printf("No leaderboard data available.\n");
        return;
    }
    char name[50];
    printf("LEADERBOARD:\n");
    printf("----------------------------\n");
    printf("Rank | Player Name\n");
    printf("----------------------------\n");
    int rank = 1;
    while (fgets(name, sizeof(name), file)) {
        name[strcspn(name, "\n")] = '\0';
        printf("%4d | %s\n", rank, name);
        rank++;
    }
    printf("----------------------------\n");
    fclose(file);
}
