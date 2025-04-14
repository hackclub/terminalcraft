#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#ifndef _WIN32
#include <unistd.h>
#else
#include <windows.h>
void usleep(__int64 usec)
{
  HANDLE timer;
  LARGE_INTEGER ft;

  ft.QuadPart = -(10 * usec); // Convert to 100 nanosecond interval, negative value indicates relative time

  timer = CreateWaitableTimer(NULL, TRUE, NULL);
  SetWaitableTimer(timer, &ft, 0, NULL, NULL, 0);
  WaitForSingleObject(timer, INFINITE);
  CloseHandle(timer);
}
#endif
#include <string.h>
#ifdef _WIN32
#include <ncurses/ncurses.h>
#else
#include <ncurses.h> // Linux ncurses
#endif


#define PI 3.14159265359f

// Global variables
float A = 0, B = 0, C = 0;
float cubeWidth;
int width, height;
float *zBuffer;
char *buffer;
int distanceFromCam = 100;
float K1 = 40;
int r = 0;
float cameraY = 0; // Camera Y position

// Function prototypes
float calculateX(float i, float j, float k);
float calculateY(float i, float j, float k);
float calculateZ(float i, float j, float k);
void calculateForPoint(float i, float j, float k, int ch);
void globRotX(float t);
void globRotY(float t);
void init_ncurses();
void cleanup();
void render();
void handleInput();

// 3D transformation functions
float calculateX(float i, float j, float k) {
    return j * sin(A) * sin(B) * cos(C) - k * cos(A) * sin(B) * cos(C) + j * cos(A) * sin(C) + k * sin(A) * sin(C) + i * cos(B) * cos(C);
}

float calculateY(float i, float j, float k) {
    return j * cos(A) * cos(C) + k * sin(A) * cos(C) - j * sin(A) * sin(B) * sin(C) + k * cos(A) * sin(B) * sin(C) - i * cos(B) * sin(C);
}

float calculateZ(float i, float j, float k) {
    return k * cos(A) * sin(B) - j * sin(A) * cos(B) + i * sin(B);
}

void calculateForPoint(float i, float j, float k, int ch) {
    float x = calculateX(i, j, k);
    float y = calculateY(i, j, k);
    float z = calculateZ(i, j, k) + distanceFromCam;
    float ooz = 1 / z;
    int xp = (int)(width / 2 + K1 * ooz * x * 2);
    int yp = (int)(height / 2 + K1 * ooz * y);

    if (xp >= 0 && xp < width && yp >= 0 && yp < height) {
        int idx = xp + yp * width;
        if (ooz > zBuffer[idx]) {
            zBuffer[idx] = ooz;
            buffer[idx] = ch;
        }
    }
}

// Rotation functions. 
// Credits: https://www.geometrictools.com/Documentation/EulerAngles.pdf, 
// https://www.symbolab.com/solver/step-by-step/%5Cbegin%7Bpmatrix%7D1%260%260%5C%5C%20%20%20%200%26cos%5Cleft(A%5Cright)%26-sin%5Cleft(A%5Cright)%5C%5C%20%20%20%200%26sin%5Cleft(A%5Cright)%26cos%5Cleft(A%5Cright)%5Cend%7Bpmatrix%7D%5Cbegin%7Bpmatrix%7Dcos%5Cleft(B%5Cright)%260%26sin%5Cleft(B%5Cright)%5C%5C%20%20%20%200%261%260%5C%5C%20%20%20%20-sin%5Cleft(B%5Cright)%260%26cos%5Cleft(B%5Cright)%5Cend%7Bpmatrix%7D%5Cbegin%7Bpmatrix%7Dcos%5Cleft(C%5Cright)%26-sin%5Cleft(C%5Cright)%260%5C%5C%20%20%20%20sin%5Cleft(C%5Cright)%26cos%5Cleft(C%5Cright)%260%5C%5C%20%20%20%200%260%261%5Cend%7Bpmatrix%7D%5Cbegin%7Bpmatrix%7D1%260%260%5C%5C%20%20%20%20%200%26cos%5Cleft(t%5Cright)%26-sin%5Cleft(t%5Cright)%5C%5C%20%20%20%20%200%26sin%5Cleft(t%5Cright)%26cos%5Cleft(t%5Cright)%5Cend%7Bpmatrix%7D?or=input, 
// https://www.symbolab.com/solver/step-by-step/%5Cbegin%7Bpmatrix%7D1%260%260%5C%5C%20%20%200%26cos%5Cleft(A%5Cright)%26-sin%5Cleft(A%5Cright)%5C%5C%20%20%200%26sin%5Cleft(A%5Cright)%26cos%5Cleft(A%5Cright)%5Cend%7Bpmatrix%7D%5Cbegin%7Bpmatrix%7Dcos%5Cleft(B%5Cright)%260%26sin%5Cleft(B%5Cright)%5C%5C%20%20%200%261%260%5C%5C%20%20%20-sin%5Cleft(B%5Cright)%260%26cos%5Cleft(B%5Cright)%5Cend%7Bpmatrix%7D%5Cbegin%7Bpmatrix%7Dcos%5Cleft(C%5Cright)%26-sin%5Cleft(C%5Cright)%260%5C%5C%20%20%20sin%5Cleft(C%5Cright)%26cos%5Cleft(C%5Cright)%260%5C%5C%20%20%200%260%261%5Cend%7Bpmatrix%7D%5Cbegin%7Bpmatrix%7Dcos%5Cleft(t%5Cright)%260%26sin%5Cleft(t%5Cright)%5C%5C%20%20%20%200%261%260%5C%5C%20%20%20%20-sin%5Cleft(t%5Cright)%260%26cos%5Cleft(t%5Cright)%5Cend%7Bpmatrix%7D?or=input
void globRotX(float t) {
    float r00 = cos(B) * cos(C);
    float r01 = sin(B) * sin(t) - cos(B) * sin(C) * cos(t);
    float r02 = cos(B) * sin(C) * sin(t) + sin(B) * cos(t);
    float r10 = sin(A) * sin(B) * cos(C) + cos(A) * sin(C);
    float r11 = cos(t) * (cos(A) * cos(C) - sin(A) * sin(B) * sin(C)) - sin(A) * cos(B) * sin(t);
    float r12 = -sin(t) * (cos(A) * cos(C) - sin(A) * sin(B) * sin(C)) - sin(A) * cos(B) * cos(t);
    float r22 = cos(A) * cos(B) * cos(t) - sin(t) * (cos(A) * sin(B) * sin(C) + sin(A) * cos(C));
    
    if (r02 < +1) {
        if (r02 > -1) {
            B = asin(r02);
            A = atan2(-r12, r22);
            C = atan2(-r01, r00);
        } else {
            B = -PI/2;
            A = -atan2(r10,r11);
            C = 0;
        }
    } else {
        B = +PI/2;
        A = atan2(r10,r11);
        C = 0;
    }
}

void globRotY(float t) {
    float r00 = cos(B) * cos(C) * cos(t) - sin(B) * sin(t);
    float r01 = -cos(B) * sin(C);
    float r02 = cos(B) * cos(C) * sin(t) + sin(B) * cos(t);
    float r10 = cos(t) * (sin(A) * sin(B) * cos(C) + cos(A) * sin(C)) + sin(A) * cos(B) * sin(t);
    float r11 = cos(A) * cos(C) - sin(A) * sin(B) * sin(C);
    float r12 = sin(t) * (sin(A) * sin(B) * cos(C) + cos(A) * sin(C)) - sin(A) * cos(B) * cos(t);
    float r22 = sin(t) * (sin(A) * sin(C) - cos(A) * sin(B) * cos(C)) + cos(A) * cos(B) * cos(t);
    
    if (r02 < 1) {
        if (r02 > -1) {
            B = asin(r02);
            A = atan2(-r12, r22);
            C = atan2(-r01, r00);
        } else {
            B = -PI/2;
            A = -atan2(r10,r11);
            C = 0;
        }
    } else {
        B = PI/2;
        A = atan2(r10,r11);
        C = 0;
    }
}

// Initialize ncurses
void init_ncurses() {
    initscr();
    raw(); // Allows capturing control characters
    noecho();
    nodelay(stdscr, TRUE);
    keypad(stdscr, TRUE);
    curs_set(0); // Hide cursor

    // Set initial screen size
    getmaxyx(stdscr, height, width);
}

// Cleanup function
void cleanup() {
    free(zBuffer);
    free(buffer);
    endwin();
}

// Render the frame
void render() {
    clear(); // More efficient than clear()
    
    memset(buffer, ' ', width * height);
    memset(zBuffer, 0, width * height * sizeof(float));

    for (float i = -cubeWidth / 2; i < cubeWidth / 2; i += 0.6) {
        for (float j = -cubeWidth / 2; j < cubeWidth / 2; j += 0.6) {
            calculateForPoint(i, j - cameraY, -cubeWidth / 2, '@');
            calculateForPoint(cubeWidth / 2, j - cameraY, i, '$');
            calculateForPoint(-cubeWidth / 2, j - cameraY, -i, '~');
            calculateForPoint(-i, j - cameraY, cubeWidth / 2, '#');
            calculateForPoint(i, -cubeWidth / 2 - cameraY, -j, ';');
            calculateForPoint(i, cubeWidth / 2 - cameraY, j - cameraY, '+');
        }
    }

    for (int k = 0; k < width * height; k++) {
        if (k % width) {
            addch(buffer[k]);
        } else {
            addch('\n');
        }
    }

    refresh();
}

// Handle keyboard input
void handleInput() {
    int ch = getch();
    if (ch == 'r') r = !r;
    else if (ch == KEY_UP) globRotX(0.05);
    else if (ch == KEY_DOWN) globRotX(-0.05);
    else if (ch == KEY_LEFT) globRotY(0.05);
    else if (ch == KEY_RIGHT) globRotY(-0.05);
    else if (ch == 'q') {
        cleanup();
        exit(0);
    }
}

// Function to handle screen resize
void handleResize() {
    int newH, newW;
    getmaxyx(stdscr, newH, newW);
    
    if (newH != height || newW != width) {
        height = newH;
        width = newW;

        free(zBuffer);
        free(buffer);

        zBuffer = (float *)malloc(width * height * sizeof(float));
        buffer = (char *)malloc(width * height * sizeof(char));

        if (!zBuffer || !buffer) {
            cleanup();
            fprintf(stderr, "Memory allocation failed\n");
            exit(1);
        }

        cubeWidth = (float)fmin(width, height) * 0.8f;
        if ((int)cubeWidth % 2 != 0) cubeWidth -= 1;
    }
}

int main() {
    init_ncurses();

    cubeWidth = (float)fmin(width, height) * 0.8f;
    if ((int)cubeWidth % 2 != 0) cubeWidth -= 1;

    zBuffer = (float *)malloc(width * height * sizeof(float));
    buffer = (char *)malloc(width * height * sizeof(char));

    if (!zBuffer || !buffer) {
        cleanup();
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    while (1) {
        handleResize();
        handleInput();
        render();

        if (r) {
            A += 0.05;
            B += 0.05;
            C += 0.01;
        }
        usleep(16000);
    }

    cleanup();
    return 0;
}
