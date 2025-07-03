#ifndef XNOTE_H
#define XNOTE_H

#include "xsh.h"

/**
 * @brief A secure, command-line note-taking utility that allows users to create, 
 * view, encrypt, list, and delete notes directly from the shell.
 * 
 * @param args Null-terminated array of strings representing the command and its arguments.
 * @return int Returns 1 to continue shell execution.
 */

int xsh_xnote(char **args);

#endif // XNOTE_H