#include "network.h"

// Implementation of network client functionality
int xsh_client(char **args) {
#ifdef _WIN32
    WSADATA wsaData;
    SOCKET connectSocket = INVALID_SOCKET;
    struct sockaddr_in serverAddr;
    char *sendMessage = "XenoGate2025"; // Initial message
    char recvBuffer[BUFFER_SIZE];
    int iResult;

    // 1. Initialize Winsock
    iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        printf("[!] WSAStartup failed: %d\n", iResult);
        return 1;
    }
    printf("[*] Winsock initialized.\n");

    // 2. Create a socket
    connectSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (connectSocket == INVALID_SOCKET) {
        printf("[!] socket failed with error: %d\n", WSAGetLastError()); // Changed %ld to %d
        WSACleanup();
        return 1;
    }
    printf("[*] Socket created.\n");

    // 3. Prepare the sockaddr_in structure for the server
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(SERVER_PORT);
    if (inet_pton(AF_INET, SERVER_IP, &serverAddr.sin_addr) <= 0) {
        printf("[!] inet_pton failed or invalid IP address: %s\n", SERVER_IP);
        closesocket(connectSocket);
        WSACleanup();
        return 1;
    }
    printf("[*] Server address prepared: %s:%d\n", SERVER_IP, SERVER_PORT);

    // 4. Connect to server
    iResult = connect(connectSocket, (struct sockaddr *)&serverAddr, sizeof(serverAddr));
    if (iResult == SOCKET_ERROR) {
        printf("[!] connect failed with error: %d\n", WSAGetLastError()); // Changed %ld to %d
        closesocket(connectSocket);
        WSACleanup();
        return 1;
    }
    printf("[*] Connected to server.\n");

    // 5. Send initial data
    iResult = send(connectSocket, sendMessage, (int)strlen(sendMessage), 0);
    if (iResult == SOCKET_ERROR) {
        printf("[!] send failed with error: %d\n", WSAGetLastError()); // Changed %ld to %d
        closesocket(connectSocket);
        WSACleanup();
        return 1;
    }
    printf("[*] Bytes Sent: %d\n[*] Sent message: %s\n", iResult, sendMessage);

    // 6. Receive initial response
    iResult = recv(connectSocket, recvBuffer, BUFFER_SIZE - 1, 0);
    if (iResult > 0) {
        recvBuffer[iResult] = '\0';
        printf("[*] Bytes received: %d\n[*] Received message: %s\n", iResult, recvBuffer);
    } else if (iResult == 0) {
        printf("[!] Connection closed by server.\n");
    } else {
        printf("[!] recv failed with error: %d\n", WSAGetLastError()); // Changed %ld to %d
    }

    // Interactive loop for sending/receiving messages
    char *input = malloc(BUFFER_SIZE);
    if (!input) {
        printf("[!] Memory allocation failed for input buffer.\n");
        closesocket(connectSocket);
        WSACleanup();
        return 1;
    }

    while(1) {
        printf("[*] Enter a message to send (or 'exit' to quit): ");
        
        // Read user input safely
        if (fgets(input, BUFFER_SIZE, stdin) == NULL) {
            // EOF or read error
            printf("\n[!] Input error or EOF. Exiting client input loop.\n");
            break;
        }
        input[strcspn(input, "\r\n")] = 0; // Remove trailing newline

        if (strcmp(input, "exit") == 0) {
            break; 
        }
        if (strlen(input) == 0) {
            continue; // Skip empty input
        }

        // Send user input
        iResult = send(connectSocket, input, (int)strlen(input), 0);
        if (iResult == SOCKET_ERROR) {
            printf("[!] send failed with error: %d\n", WSAGetLastError()); // Changed %ld to %d
            break; // Break on send error
        }
        printf("[*] Bytes Sent: %d\n[*] Sent message: %s\n", iResult, input);

        // Receive response from server
        iResult = recv(connectSocket, recvBuffer, BUFFER_SIZE - 1, 0);
        if (iResult > 0) {
            recvBuffer[iResult] = '\0';
            printf("[*] Bytes received: %d\n[*] Received message: %s\n", iResult, recvBuffer);
        } else if (iResult == 0) {
            printf("[!] Connection closed by server.\n");
            break;
        } else {
            printf("[!] recv failed with error: %d\n", WSAGetLastError()); // Changed %ld to %d
            break;
        }
    }

    free(input);
    // 7. Cleanup
    closesocket(connectSocket);
    WSACleanup();
    printf("[*] Connection closed and Winsock cleaned up.\n");

#else
    // POSIX (Linux/macOS) implementation
    int sock = 0;
    struct sockaddr_in serv_addr;
    char *sendMessage = "XenoGate2025"; // Initial message
    char buffer[BUFFER_SIZE] = {0};

    // 1. Create socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        printf("\n [!] Socket creation error \n");
        return 1;
    }
    printf("[*] Socket created.\n");

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(SERVER_PORT);

    // 2. Convert IPv4 and IPv6 addresses from text to binary form
    if(inet_pton(AF_INET, SERVER_IP, &serv_addr.sin_addr) <= 0) {
        printf("\n[!] Invalid address/ Address not supported: %s\n", SERVER_IP);
        close(sock);
        return 1;
    }
    printf("[*] Server address prepared: %s:%d\n", SERVER_IP, SERVER_PORT);

    // 3. Connect to server
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        printf("\n[!] Connection Failed \n");
        perror("connect");
        close(sock);
        return 1;
    }
    printf("[*] Connected to server.\n");

    // 4. Send initial data
    ssize_t bytes_sent = send(sock, sendMessage, strlen(sendMessage), 0);
    if (bytes_sent < 0) {
        perror("[!] send failed");
        close(sock);
        return 1;
    }
    printf("[*] Bytes Sent: %zd\n[*] Sent message: %s\n", bytes_sent, sendMessage);

    // 5. Receive initial response
    ssize_t valread = read(sock, buffer, BUFFER_SIZE - 1);
    if (valread > 0) {
        buffer[valread] = '\0';
        printf("[*] Bytes received: %zd\n[*] Received message: %s\n", valread, buffer);
    } else if (valread == 0) {
        printf("[!] Connection closed by server.\n");
    } else {
        perror("[!] read failed");
    }

    // Interactive loop for sending/receiving messages
    char *input_line = malloc(BUFFER_SIZE);
    if (!input_line) {
        printf("[!] Memory allocation failed for input buffer.\n");
        close(sock);
        return 1;
    }

    while(1) {
        printf("[*] Enter a message to send (or 'exit' to quit): ");
        if (fgets(input_line, BUFFER_SIZE, stdin) == NULL) {
            printf("\n[!] Input error or EOF. Exiting client input loop.\n");
            break;
        }
        input_line[strcspn(input_line, "\r\n")] = 0; // Remove trailing newline

        if (strcmp(input_line, "exit") == 0) {
            break;
        }
        if (strlen(input_line) == 0) {
            continue; // Skip empty input
        }

        // Send user input
        bytes_sent = send(sock, input_line, strlen(input_line), 0);
        if (bytes_sent < 0) {
            perror("[!] send failed");
            break;
        }
        printf("[*] Bytes Sent: %zd\n[*] Sent message: %s\n", bytes_sent, input_line);

        // Receive response from server
        valread = read(sock, buffer, BUFFER_SIZE - 1);
        if (valread > 0) {
            buffer[valread] = '\0';
            printf("[*] Bytes received: %zd\n[*] Received message: %s\n", valread, buffer);
        } else if (valread == 0) {
            printf("[!] Connection closed by server.\n");
            break;
        } else {
            perror("[!] read failed");
            break;
        }
    }

    free(input_line);
    // 6. Close the socket
    close(sock);
    printf("[*] Connection closed.\n");
#endif
    return 1; // Indicate to the shell loop to continue.
}
