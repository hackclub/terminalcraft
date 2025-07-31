#ifndef NETWORK_H
#define NETWORK_H

// Socket related includes, platform-dependent
#ifdef _WIN32
    #define WIN32_LEAN_AND_MEAN
    #include <winsock2.h> // Include winsock2.h before xsh.h (which might include windows.h)
    #include <ws2tcpip.h> // For inet_pton and other newer functions
    // Need to link with Ws2_32.lib
    #pragma comment(lib, "Ws2_32.lib")
#endif

#include "xsh.h" // For common definitions, BUFFER_SIZE, SERVER_IP, SERVER_PORT

#ifndef _WIN32 // For non-Windows, include these after xsh.h
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <unistd.h> // For close()
#endif

// Function prototype for network.c
int xsh_client(char **args);

#endif // NETWORK_H
