#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include <stdbool.h>

char getCharNoEcho();
int getMenuSelection(const char* title, const char** options, int optionCount, bool allowEsc);
char* getString(const char* prompt);
char* processPath(const char* path, bool mustExist);
bool fileExists(const char* path);
char* readFileContent(const char* filename, size_t* contentLength);
char* getCurrentWorkingDirectory();
void infoHandler(void);

void testHandler(void);
bool createFile(const char* filename);

#endif // FUNCTIONS_H