#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <ctype.h>

char board[3][3];
char PLAYER, PLAYER2, COMPUTER;
int is_multiplayer = 0;

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

int main(){
    char response;
    do {
        menu();
        selectMode();
        character();
        char winner = ' ';
        resetBoard();
    
        while(winner == ' ' && getFreeSpaces() != 0){
            printBoard();
            playerMove(1);
    
            winner = checkWinner();
            if(winner != ' ' || getFreeSpaces() == 0){
                break;
            }
    
            if (is_multiplayer) {
                playerMove(2);
            } else {
                computerMove();
            }
    
            winner = checkWinner();
            if(winner != ' ' || getFreeSpaces() == 0){
                break;
            }
        }
        printBoard();
        printWinner(winner);

        printf("\nWould you like to play again? (Y/N): ");
        scanf(" %c", &response);
        response = toupper(response);
    } while (response == 'Y');

    printf("Thanks for playing!\n");
    return 0;
}

void resetBoard(){
    for(int i = 0; i < 3; i++){
        for(int j = 0; j < 3; j++){
            board[i][j] = ' ';
        }
    }
}

void printBoard(){
    printf("\n");
    for(int i = 0; i < 3; i++){
        printf("  %c  |  %c  |  %c  \n", board[i][0], board[i][1], board[i][2]);
        if(i < 2) printf("-----|-----|-----\n");
    }
    printf("\n");
}

int getFreeSpaces(){
    int freespaces = 9;
    for(int i = 0; i < 3; i++){
        for(int j = 0; j < 3; j++){
            if(board[i][j] != ' '){
                freespaces--;
            }
        }
    }
    return freespaces;
}

void playerMove(int player){
    int x, y;
    char symbol = (player == 1) ? PLAYER : PLAYER2;

    do {
        printf("Player %d (%c), enter row #(1-3): ", player, symbol);
        scanf("%d", &x);
        x--;
        printf("Enter column #(1-3): ");
        scanf("%d", &y);
        y--;
    
        if(board[x][y] != ' '){
            printf("Invalid move, try again.\n");
        } else {
            board[x][y] = symbol;
            break;
        }
    } while (1);
}

void computerMove(){
    srand(time(0));
    int x, y;
    printf("Computer is thinking...\n");
    
    if(getFreeSpaces() > 0){
        do {
            x = rand() % 3;
            y = rand() % 3;
        } while (board[x][y] != ' ');
        board[x][y] = COMPUTER;
    }
}

char checkWinner(){
    for(int i = 0; i < 3; i++){
        if(board[i][0] == board[i][1] && board[i][0] == board[i][2] && board[i][0] != ' ')
            return board[i][0];
        if(board[0][i] == board[1][i] && board[0][i] == board[2][i] && board[0][i] != ' ')
            return board[0][i];
    }
    if(board[0][0] == board[1][1] && board[0][0] == board[2][2] && board[0][0] != ' ')
        return board[0][0];
    if(board[0][2] == board[1][1] && board[0][2] == board[2][0] && board[0][2] != ' ')
        return board[0][2];
    return ' ';
}

void printWinner(char winner){
    if(winner == PLAYER){
        printf("PLAYER 1 WINS!\n");
    }
    else if(winner == PLAYER2){
        printf("PLAYER 2 WINS!\n");
    }
    else if(winner == COMPUTER){
        printf("COMPUTER WINS!\n");
    }
    else{
        printf("IT'S A TIE!\n");
    }
}

void menu(){
    char response;
    printf("\nWELCOME TO TIC-TAC-TOE\n");
    printf("Do you want to play? (Y/N): ");
    scanf(" %c", &response);
    response = toupper(response);
    if(response != 'Y'){
        printf("You have exited the game!\n");
        exit(0);
    }
}

void selectMode(){
    int choice;
    printf("Select Mode: \n1. Single Player (vs AI)\n2. Multiplayer (Two Players)\nEnter choice: ");
    scanf("%d", &choice);
    is_multiplayer = (choice == 2);
}

void character(){
    char response;
    printf("\nChoose your symbol (X/O): ");
    scanf(" %c", &response);
    response = toupper(response);
    PLAYER = (response == 'X') ? 'X' : 'O';
    if(is_multiplayer) {
        PLAYER2 = (PLAYER == 'X') ? 'O' : 'X';
    } else {
        COMPUTER = (PLAYER == 'X') ? 'O' : 'X';
    }
}
