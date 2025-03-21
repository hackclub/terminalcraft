#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include <stdbool.h>

char getCharNoEcho();
int getMenuSelection(const char* title, const char** options, int optionCount, bool allowEsc);
char* getString(const char* prompt);
char* processPath(const char* path, bool mustExist, bool isDirectory);
bool fileExists(const char* path);
char* readFileContent(const char* filename, size_t* contentLength, bool isBinary);
char* getCurrentWorkingDirectory();
void infoHandler(void);

void testHandler(void);
bool createFile(const char* filename);
bool changeWorkingDirectory(const char* newDir);
void changeDirHandler(void);

void configHandler(const char* configFile);
bool parseConfigFile(const char* content);

void sigHandler(int signum);

#endif // FUNCTIONS_H