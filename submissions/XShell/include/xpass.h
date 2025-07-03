#ifndef XPASS_H
#define XPASS_H

#include "xsh.h"

/**
 * @brief A password management tool for generating cryptographically secure passwords 
 * with customizable complexity and analyzing the strength of any password via entropy calculation.
 * 
 * @param args Null-terminated array of strings representing the command and its arguments.
 * @return int Returns 1 to continue shell execution.
 */
int xsh_xpass(char **args);

#endif // XPASS_H