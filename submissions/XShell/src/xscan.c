#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <stdint.h>
#include <ctype.h> // For isprint and isspace

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <sys/select.h>
#endif

#include "xscan.h"

// Constants
#define MAX_THREADS 200
#define DEFAULT_TIMEOUT_SEC 3
#define BANNER_BUF_SIZE 1024

// Cross-platform definitions
#ifdef _WIN32
#define close closesocket
typedef HANDLE thread_t;
typedef CRITICAL_SECTION mutex_t;
#define THREAD_FUNC_RETURN_TYPE DWORD WINAPI
#define THREAD_FUNC_ARGS LPVOID
#else
typedef pthread_t thread_t;
typedef pthread_mutex_t mutex_t;
#define THREAD_FUNC_RETURN_TYPE void*
#define THREAD_FUNC_ARGS void*
#endif

// IP and TCP header structures (for Windows, as they aren't in the headers)
#ifdef _WIN32
struct ip {
    unsigned char  ip_hl:4, ip_v:4;
    unsigned char  ip_tos;
    unsigned short ip_len;
    unsigned short ip_id;
    unsigned short ip_off;
    unsigned char  ip_ttl;
    unsigned char  ip_p;
    unsigned short ip_sum;
    struct in_addr ip_src;
    struct in_addr ip_dst;
};

struct tcphdr {
    unsigned short th_sport;
    unsigned short th_dport;
    uint32_t   th_seq;
    uint32_t   th_ack;
    unsigned char  th_off:4, th_x2:4;
    unsigned char  th_flags;
    unsigned short th_win;
    unsigned short th_sum;
    unsigned short th_urp;
};
#ifndef TH_SYN
#define TH_SYN 0x02
#endif
#ifndef TH_ACK
#define TH_ACK 0x10
#endif
#ifndef TH_RST
#define TH_RST 0x04
#endif
#endif

// Pseudo header for checksum calculation
struct pseudo_header {
    uint32_t source_address;
    uint32_t dest_address;
    uint8_t  placeholder;
    uint8_t  protocol;
    uint16_t tcp_length;
};

// Port state enum and info struct
enum port_state { P_UNKNOWN, P_SENT, P_OPEN, P_CLOSED };
struct port_info {
    enum port_state state;
    char banner[BANNER_BUF_SIZE];
};

// --- Global Variables ---
static struct port_info port_statuses[65536];
static const char *target_ip_g = NULL;
static char source_ip_g[INET_ADDRSTRLEN];
static int start_port_g = 0;
static int end_port_g = 0;
static volatile int stop_listening = 0;
static int next_port_to_scan = 0;

// Threading and synchronization
static thread_t sender_threads[MAX_THREADS];
static thread_t listener_thread;
static mutex_t port_mutex;
static mutex_t status_mutex;

// --- Function Prototypes ---
void send_syn(const char *source_ip, const char *dest_ip, int port);
unsigned short csum(unsigned short *ptr, int nbytes);
void process_packet(const unsigned char* buffer, int size);
void print_usage();
void initialize_mutex(mutex_t *mutex);
void lock_mutex(mutex_t *mutex);
void unlock_mutex(mutex_t *mutex);
void destroy_mutex(mutex_t *mutex);
THREAD_FUNC_RETURN_TYPE sender_thread_func(THREAD_FUNC_ARGS arg);
THREAD_FUNC_RETURN_TYPE listener_thread_func(THREAD_FUNC_ARGS arg);
THREAD_FUNC_RETURN_TYPE banner_grabber_thread_func(THREAD_FUNC_ARGS arg);


// --- Main Logic ---
int xscan_main(int argc, char **argv) {
#ifdef _WIN32
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2,2), &wsa) != 0) {
        fprintf(stderr, "WSAStartup failed. Error Code : %d\n", WSAGetLastError());
        return 1;
    }
#endif
    srand((unsigned int)time(NULL));

    if (argc < 3 || argc > 4) {
        print_usage();
        return 1;
    }

    target_ip_g = argv[1];
    start_port_g = atoi(argv[2]);
    end_port_g = (argc == 4) ? atoi(argv[3]) : start_port_g;
    next_port_to_scan = start_port_g;

    if (start_port_g <= 0 || end_port_g <= 0 || start_port_g > 65535 || end_port_g > 65535 || start_port_g > end_port_g) {
        fprintf(stderr, "Invalid port range.\n");
        return 1;
    }

    // Initialize port statuses
    for (int i = 0; i < 65536; i++) {
        port_statuses[i].state = P_UNKNOWN;
        memset(port_statuses[i].banner, 0, BANNER_BUF_SIZE);
    }

    // Initialize mutexes
    initialize_mutex(&port_mutex);
    initialize_mutex(&status_mutex);

    // --- Dynamically determine source IP ---
    strcpy(source_ip_g, "127.0.0.1"); // Fallback
    int temp_sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (temp_sock >= 0) {
        struct sockaddr_in serv;
        memset(&serv, 0, sizeof(serv));
        serv.sin_family = AF_INET;
        serv.sin_addr.s_addr = inet_addr(target_ip_g);
        serv.sin_port = htons(80); // Connect to a common port
        if (connect(temp_sock, (struct sockaddr*)&serv, sizeof(serv)) == 0) {
            struct sockaddr_in name;
            socklen_t namelen = sizeof(name);
            if (getsockname(temp_sock, (struct sockaddr*)&name, &namelen) == 0) {
                inet_ntop(AF_INET, &name.sin_addr, source_ip_g, sizeof(source_ip_g));
            }
        }
        close(temp_sock);
    }
    printf("Using source IP: %s\n", source_ip_g);

    // --- Start Scanner ---
    int sock_raw = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
    if (sock_raw < 0) {
        perror("socket (raw)");
        fprintf(stderr, "Raw socket creation failed. Try running with sudo/administrator privileges.\n");
        return 1;
    }

    printf("Starting scan on %s (ports %d-%d) with %d threads...\n", target_ip_g, start_port_g, end_port_g, MAX_THREADS);

    // Start listener thread
#ifdef _WIN32
    listener_thread = CreateThread(NULL, 0, listener_thread_func, (LPVOID)(intptr_t)sock_raw, 0, NULL);
#else
    pthread_create(&listener_thread, NULL, listener_thread_func, (void*)(intptr_t)sock_raw);
#endif

    // Start sender threads
    for (int i = 0; i < MAX_THREADS; i++) {
#ifdef _WIN32
        sender_threads[i] = CreateThread(NULL, 0, sender_thread_func, NULL, 0, NULL);
#else
        pthread_create(&sender_threads[i], NULL, sender_thread_func, NULL);
#endif
    }

    // Wait for sender threads to finish
    for (int i = 0; i < MAX_THREADS; i++) {
#ifdef _WIN32
        WaitForSingleObject(sender_threads[i], INFINITE);
        CloseHandle(sender_threads[i]);
#else
        pthread_join(sender_threads[i], NULL);
#endif
    }

    printf("\nAll packets sent. Waiting %d seconds for replies...\n", DEFAULT_TIMEOUT_SEC);
    fflush(stdout);
#ifdef _WIN32
    Sleep(DEFAULT_TIMEOUT_SEC * 1000);
#else
    sleep(DEFAULT_TIMEOUT_SEC);
#endif

    // Stop listener and clean up
    stop_listening = 1;
#ifdef _WIN32
    WaitForSingleObject(listener_thread, INFINITE);
    CloseHandle(listener_thread);
#else
    pthread_join(listener_thread, NULL);
#endif
    close(sock_raw);

    // --- Report Results ---
    printf("\nScan Results:\n");
    for (int port = start_port_g; port <= end_port_g; port++) {
        switch (port_statuses[port].state) {
            case P_OPEN:
                printf("Port %d: Open\n", port);
                if (strlen(port_statuses[port].banner) > 0) {
                    // Sanitize banner before printing
                    char clean_banner[BANNER_BUF_SIZE];
                    int j = 0;
                    for(int i = 0; port_statuses[port].banner[i] != '\0' && j < BANNER_BUF_SIZE -1; i++) {
                        if(isprint(port_statuses[port].banner[i]) || isspace(port_statuses[port].banner[i])) {
                            clean_banner[j++] = port_statuses[port].banner[i];
                        }
                    }
                    clean_banner[j] = '\0';
                    printf("  Banner: %s\n", clean_banner);
                }
                break;
            case P_CLOSED:
                printf("Port %d: Closed\n", port);
                break;
            case P_SENT: // No response received
                printf("Port %d: Filtered\n", port);
                break;
            case P_UNKNOWN: // Should not happen if sender worked
                // printf("Port %d: Unknown/Not Scanned\n", port);
                break;
        }
    }

    destroy_mutex(&port_mutex);
    destroy_mutex(&status_mutex);
#ifdef _WIN32
    WSACleanup();
#endif
    return 0;
}

// --- Thread Functions ---

THREAD_FUNC_RETURN_TYPE listener_thread_func(THREAD_FUNC_ARGS arg) {
    int sock = (int)(intptr_t)arg;
    unsigned char buffer[65536];

    while (!stop_listening) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(sock, &read_fds);

        struct timeval timeout;
        timeout.tv_sec = 1;
        timeout.tv_usec = 0;

        int activity = select(sock + 1, &read_fds, NULL, NULL, &timeout);

        if (activity < 0) {
#ifndef _WIN32
            if (errno == EINTR) continue;
#endif
            perror("select");
            break;
        }

        if (activity > 0 && FD_ISSET(sock, &read_fds)) {
            int data_size = recvfrom(sock, buffer, sizeof(buffer), 0, NULL, NULL);
            if (data_size > 0) {
                process_packet(buffer, data_size);
            }
        }
    }
    return 0;
}

THREAD_FUNC_RETURN_TYPE sender_thread_func(THREAD_FUNC_ARGS arg) {
    while (1) {
        lock_mutex(&port_mutex);
        int port = next_port_to_scan++;
        unlock_mutex(&port_mutex);

        if (port > end_port_g) {
            break;
        }

        send_syn(source_ip_g, target_ip_g, port);

        lock_mutex(&status_mutex);
        if (port_statuses[port].state == P_UNKNOWN) {
            port_statuses[port].state = P_SENT;
        }
        unlock_mutex(&status_mutex);
    }
    return 0;
}

THREAD_FUNC_RETURN_TYPE banner_grabber_thread_func(THREAD_FUNC_ARGS arg) {
    int port = (int)(intptr_t)arg;
    struct sockaddr_in dest_addr;
    int sock = socket(AF_INET, SOCK_STREAM, 0);

    if (sock < 0) return 0;

    dest_addr.sin_family = AF_INET;
    dest_addr.sin_addr.s_addr = inet_addr(target_ip_g);
    dest_addr.sin_port = htons(port);

    // Set a timeout for the connection attempt
#ifdef _WIN32
    DWORD timeout = 2000; // 2 seconds
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (const char*)&timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&timeout, sizeof(timeout));
#else
    struct timeval timeout;
    timeout.tv_sec = 2;
    timeout.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
#endif

    if (connect(sock, (struct sockaddr*)&dest_addr, sizeof(dest_addr)) == 0) {
        char buffer[BANNER_BUF_SIZE] = {0};
        // Send a generic probe for HTTP
        send(sock, "GET / HTTP/1.0\r\n\r\n", 19, 0);
        int received = recv(sock, buffer, sizeof(buffer) - 1, 0);
        if (received > 0) {
            lock_mutex(&status_mutex);
            strncpy(port_statuses[port].banner, buffer, received);
            port_statuses[port].banner[received] = '\0';
            unlock_mutex(&status_mutex);
        }
    }

    close(sock);
    return 0;
}


// --- Network Utility Functions ---

void process_packet(const unsigned char* buffer, int size) {
    struct ip *iph = (struct ip*)buffer;
    if (iph->ip_src.s_addr != inet_addr(target_ip_g)) {
        return; // Not from our target
    }

    if (iph->ip_p == IPPROTO_TCP) {
        unsigned short iphdrlen = iph->ip_hl * 4;
        if (size < iphdrlen + sizeof(struct tcphdr)) {
            return; // Packet too small
        }
        struct tcphdr *tcph = (struct tcphdr*)(buffer + iphdrlen);
        int source_port = ntohs(tcph->th_sport);

        if (source_port >= start_port_g && source_port <= end_port_g) {
            lock_mutex(&status_mutex);
            if (port_statuses[source_port].state == P_SENT) {
                if ((tcph->th_flags & (TH_SYN | TH_ACK)) == (TH_SYN | TH_ACK)) {
                    port_statuses[source_port].state = P_OPEN;
                    // Spawn banner grabber
                    thread_t banner_thread;
#ifdef _WIN32
                    banner_thread = CreateThread(NULL, 0, banner_grabber_thread_func, (LPVOID)(intptr_t)source_port, 0, NULL);
                    CloseHandle(banner_thread); // Detach
#else
                    pthread_create(&banner_thread, NULL, banner_grabber_thread_func, (void*)(intptr_t)source_port);
                    pthread_detach(banner_thread);
#endif
                } else if (tcph->th_flags & TH_RST) {
                    port_statuses[source_port].state = P_CLOSED;
                }
            }
            unlock_mutex(&status_mutex);
        }
    }
}

void send_syn(const char *source_ip, const char *dest_ip, int port) {
    int s = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (s < 0) {
        // Don't flood with errors if it fails repeatedly
        // perror("socket (send)");
        return;
    }

    // Set the IP_HDRINCL option so we can build our own IP headers.
    // This is required on most platforms for raw socket programming.
    const int one = 1;
    if (setsockopt(s, IPPROTO_IP, IP_HDRINCL, (const char*)&one, sizeof(one)) < 0) {
        perror("setsockopt(IP_HDRINCL) failed");
        // Provide a more helpful error message.
        fprintf(stderr, "Error: setsockopt(IP_HDRINCL) failed. This program must be run as root/administrator.\n");
        close(s);
        return;
    }

    char datagram[4096];
    struct ip *iph = (struct ip *)datagram;
    struct tcphdr *tcph = (struct tcphdr *)(datagram + sizeof(struct ip));
    struct sockaddr_in sin;

    sin.sin_family = AF_INET;
    sin.sin_port = htons(port);
    sin.sin_addr.s_addr = inet_addr(dest_ip);

    memset(datagram, 0, 4096);

    // IP Header
    iph->ip_hl = 5;
    iph->ip_v = 4;
    iph->ip_tos = 0;
    iph->ip_len = sizeof(struct ip) + sizeof(struct tcphdr);
    iph->ip_id = htonl(rand() % 65535);
    iph->ip_off = 0;
    iph->ip_ttl = 255;
    iph->ip_p = IPPROTO_TCP;
    iph->ip_sum = 0;
    iph->ip_src.s_addr = inet_addr(source_ip);
    iph->ip_dst.s_addr = sin.sin_addr.s_addr;

    // TCP Header
    tcph->th_sport = htons(12345 + (rand() % 1000));
    tcph->th_dport = htons(port);
    tcph->th_seq = htonl(rand());
    tcph->th_ack = 0;
    tcph->th_off = 5;
    tcph->th_flags = TH_SYN;
    tcph->th_win = htons(5840);
    tcph->th_sum = 0;
    tcph->th_urp = 0;

    // TCP Checksum
    struct pseudo_header psd;
    psd.source_address = iph->ip_src.s_addr;
    psd.dest_address = sin.sin_addr.s_addr;
    psd.placeholder = 0;
    psd.protocol = IPPROTO_TCP;
    psd.tcp_length = htons(sizeof(struct tcphdr));

    int psize = sizeof(struct pseudo_header) + sizeof(struct tcphdr);
    char *pseudogram = malloc(psize);
    memcpy(pseudogram, (char*)&psd, sizeof(struct pseudo_header));
    memcpy(pseudogram + sizeof(struct pseudo_header), tcph, sizeof(struct tcphdr));
    tcph->th_sum = csum((unsigned short*)pseudogram, psize);
    free(pseudogram);

    // IP Checksum
    iph->ip_sum = csum((unsigned short *)datagram, iph->ip_len);

    if (sendto(s, datagram, iph->ip_len, 0, (struct sockaddr *)&sin, sizeof(sin)) < 0) {
        // perror("sendto");
    }
    close(s);
}

unsigned short csum(unsigned short *ptr, int nbytes) {
    long sum = 0;
    unsigned short oddbyte;
    short answer;

    while (nbytes > 1) {
        sum += *ptr++;
        nbytes -= 2;
    }

    if (nbytes == 1) {
        oddbyte = 0;
        *((unsigned char *)&oddbyte) = *(unsigned char *)ptr;
        sum += oddbyte;
    }

    sum = (sum >> 16) + (sum & 0xffff);
    sum += (sum >> 16);
    answer = (short)~sum;

    return answer;
}

// --- Helper Functions ---

void print_usage() {
    printf("Usage: xscan <target IP> <start port> [end port]\n");
    printf("  target IP: The IP address of the host to scan.\n");
    printf("  start port: The first port to scan.\n");
    printf("  end port: (Optional) The last port to scan. If not provided, only the start port is scanned.\n");
}

// --- Mutex Implementation ---

void initialize_mutex(mutex_t *mutex) {
#ifdef _WIN32
    InitializeCriticalSection(mutex);
#else
    pthread_mutex_init(mutex, NULL);
#endif
}

void lock_mutex(mutex_t *mutex) {
#ifdef _WIN32
    EnterCriticalSection(mutex);
#else
    pthread_mutex_lock(mutex);
#endif
}

void unlock_mutex(mutex_t *mutex) {
#ifdef _WIN32
    LeaveCriticalSection(mutex);
#else
    pthread_mutex_unlock(mutex);
#endif
}

void destroy_mutex(mutex_t *mutex) {
#ifdef _WIN32
    DeleteCriticalSection(mutex);
#else
    pthread_mutex_destroy(mutex);
#endif
}
