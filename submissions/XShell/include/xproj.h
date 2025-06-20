#ifndef XPROJ_H
#define XPROJ_H

#include "xsh.h"

/**
 * @brief A project scaffolding utility that automates the creation of boilerplate code 
 * and directory structures for new C, Python, or web development projects.
 * 
 * @param args Null-terminated array of strings representing the command and its arguments.
 * @return int Returns 1 to continue shell execution.
 */
int xsh_xproj(char **args);

#endif // XPROJ_H