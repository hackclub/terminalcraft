#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
    #include <winsock2.h>
    #include <ws2tcpip.h>
    #include <iphlpapi.h>
    #pragma comment(lib, "iphlpapi.lib")
    #pragma comment(lib, "ws2_32.lib")
    #define SLEEP_MS(ms) Sleep(ms)
    #define CLOSE_SOCKET closesocket
    typedef int socklen_t;
#else
    #include <unistd.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip_icmp.h>
    #include <arpa/inet.h>
    #include <netdb.h>
    #include <ifaddrs.h>
    #include <sys/types.h>
    #include <sys/time.h>
    #include <net/if.h>
    #include <sys/ioctl.h>
    #define SOCKET int
    #define INVALID_SOCKET -1
    #define SOCKET_ERROR -1
    #define SLEEP_MS(ms) usleep(ms * 1000)
    #define CLOSE_SOCKET close
#endif

#include "xnet.h"

// Get current time in milliseconds (cross-platform)
unsigned long get_time_ms() {
#ifdef _WIN32
    return GetTickCount();
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (tv.tv_sec * 1000) + (tv.tv_usec / 1000);
#endif
}

#ifdef _WIN32
void show_network_info_windows() {
    PIP_ADAPTER_ADDRESSES pAddresses = NULL;
    ULONG outBufLen = 15000;
    DWORD dwRetVal = 0;

    pAddresses = (IP_ADAPTER_ADDRESSES *) malloc(outBufLen);
    if (pAddresses == NULL) {
        printf("Memory allocation failed\n");
        return;
    }

    dwRetVal = GetAdaptersAddresses(AF_UNSPEC, 0, NULL, pAddresses, &outBufLen);

    if (dwRetVal == ERROR_BUFFER_OVERFLOW) {
        free(pAddresses);
        pAddresses = (IP_ADAPTER_ADDRESSES *) malloc(outBufLen);
        if (pAddresses == NULL) {
            printf("Memory allocation failed\n");
            return;
        }
        dwRetVal = GetAdaptersAddresses(AF_UNSPEC, 0, NULL, pAddresses, &outBufLen);
    }

    if (dwRetVal == NO_ERROR) {
        PIP_ADAPTER_ADDRESSES pCurrAddresses = pAddresses;
        while (pCurrAddresses) {
            if (pCurrAddresses->OperStatus == IfOperStatusUp) {
                printf("Adapter Name: %S\n", pCurrAddresses->FriendlyName);

                PIP_ADAPTER_UNICAST_ADDRESS pUnicast = pCurrAddresses->FirstUnicastAddress;
                if (pUnicast != NULL) {
                    for (int i = 0; pUnicast != NULL; i++) {
                        if (pUnicast->Address.lpSockaddr->sa_family == AF_INET) {
                            struct sockaddr_in *sa_in = (struct sockaddr_in *) pUnicast->Address.lpSockaddr;
                            char ip_addr[INET_ADDRSTRLEN];
                            inet_ntop(AF_INET, &(sa_in->sin_addr), ip_addr, INET_ADDRSTRLEN);
                            printf("\tIP Address: %s\n", ip_addr);

                            ULONG mask;
                            ConvertLengthToIpv4Mask(pUnicast->OnLinkPrefixLength, &mask);
                            struct in_addr mask_addr;
                            mask_addr.S_un.S_addr = mask;
                            char mask_str[INET_ADDRSTRLEN];
                            inet_ntop(AF_INET, &mask_addr, mask_str, INET_ADDRSTRLEN);
                            printf("\tSubnet Mask: %s\n", mask_str);
                        }
                        pUnicast = pUnicast->Next;
                    }
                }

                printf("\tMAC Address: ");
                for (int i = 0; i < pCurrAddresses->PhysicalAddressLength; i++) {
                    if (i == (pCurrAddresses->PhysicalAddressLength - 1))
                        printf("%.2X\n", (int) pCurrAddresses->PhysicalAddress[i]);
                    else
                        printf("%.2X-", (int) pCurrAddresses->PhysicalAddress[i]);
                }
                printf("\n");
            }
            pCurrAddresses = pCurrAddresses->Next;
        }
    } else {
        printf("GetAdaptersAddresses failed with error: %d\n", dwRetVal);
    }

    if(pAddresses) {
        free(pAddresses);
    }
}
#else
void show_network_info_posix() {
    struct ifaddrs *ifaddr, *ifa;
    char host[NI_MAXHOST];
    char netmask[NI_MAXHOST];
    
    if (getifaddrs(&ifaddr) == -1) {
        perror("getifaddrs");
        return;
    }
    
    for (ifa = ifaddr; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr == NULL || !(ifa->ifa_flags & IFF_UP))
            continue;
            
        if (ifa->ifa_addr->sa_family == AF_INET) {
            printf("Adapter Name: %s\n", ifa->ifa_name);
            
            // Get IP address
            getnameinfo(ifa->ifa_addr, sizeof(struct sockaddr_in),
                        host, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
            printf("\tIP Address: %s\n", host);
            
            // Get netmask
            if (ifa->ifa_netmask != NULL) {
                getnameinfo(ifa->ifa_netmask, sizeof(struct sockaddr_in),
                            netmask, NI_MAXHOST, NULL, 0, NI_NUMERICHOST);
                printf("\tSubnet Mask: %s\n", netmask);
            }
            
            // Try to get MAC address (platform-specific)
            unsigned char mac[6];
            struct ifreq ifr;
            int sd = socket(AF_INET, SOCK_DGRAM, 0);
            if (sd != -1) {
                strcpy(ifr.ifr_name, ifa->ifa_name);
                if (ioctl(sd, SIOCGIFHWADDR, &ifr) != -1) {
                    memcpy(mac, ifr.ifr_hwaddr.sa_data, 6);
                    printf("\tMAC Address: %.2X-%.2X-%.2X-%.2X-%.2X-%.2X\n",
                           mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
                }
                close(sd);
            }
            
            printf("\n");
        }
    }
    
    freeifaddrs(ifaddr);
}
#endif

void show_network_info() {
#ifdef _WIN32
    show_network_info_windows();
#else
    show_network_info_posix();
#endif
}

// ICMP packet structure for Windows (POSIX uses the built-in structs)
#ifdef _WIN32
typedef struct _icmp_hdr {
    unsigned char icmp_type;
    unsigned char icmp_code;
    unsigned short icmp_cksum;
    unsigned short icmp_id;
    unsigned short icmp_seq;
    unsigned long icmp_timestamp;
} ICMP_HDR, *PICMP_HDR;
#endif

#define ICMP_ECHO_REQUEST 8
#define ICMP_ECHO_REPLY 0
#define ICMP_MIN 8
#define DEF_PACKET_SIZE 32
#define MAX_PACKET 1024

// Calculate checksum (works for both platforms)
unsigned short checksum(unsigned short *buffer, int size) {
    unsigned long cksum = 0;
    while (size > 1) {
        cksum += *buffer++;
        size -= sizeof(unsigned short);
    }
    if (size) {
        cksum += *(unsigned char *)buffer;
    }
    cksum = (cksum >> 16) + (cksum & 0xffff);
    cksum += (cksum >> 16);
    return (unsigned short)(~cksum);
}

void ping(char *host) {
    SOCKET sock;
    struct sockaddr_in dest, from;
    socklen_t fromlen = sizeof(from);
    char recvbuf[MAX_PACKET];
    char sendbuf[MAX_PACKET];
    int ret, bread;
    struct hostent *hp;
    unsigned int addr;
    
#ifdef _WIN32
    PICMP_HDR icmp_hdr;
#else
    struct icmp *icmp_hdr;
    int pid = getpid();
#endif

#ifdef _WIN32
    sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
#else
    sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sock != INVALID_SOCKET && getuid() != 0) {
        printf("Raw sockets require root privileges on POSIX systems\n");
        return;
    }
#endif

    if (sock == INVALID_SOCKET) {
#ifdef _WIN32
        printf("socket() failed: %d\n", WSAGetLastError());
#else
        perror("socket");
#endif
        return;
    }

    memset(&dest, 0, sizeof(dest));
    dest.sin_family = AF_INET;
    
    // First try to convert as IP address
    if (inet_pton(AF_INET, host, &dest.sin_addr) != 1) {
        // If not an IP, try to resolve hostname
        if ((hp = gethostbyname(host)) != NULL) {
            memcpy(&dest.sin_addr, hp->h_addr, hp->h_length);
        } else {
            printf("Invalid address: %s\n", host);
            CLOSE_SOCKET(sock);
            return;
        }
    }
    
    char ip_str[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &dest.sin_addr, ip_str, INET_ADDRSTRLEN);
    printf("Pinging %s [%s] with %d bytes of data:\n", host, ip_str, DEF_PACKET_SIZE);

    for (int i = 0; i < 4; i++) {
        memset(sendbuf, 0, MAX_PACKET);
        
#ifdef _WIN32
        icmp_hdr = (PICMP_HDR)sendbuf;
        icmp_hdr->icmp_type = ICMP_ECHO_REQUEST;
        icmp_hdr->icmp_code = 0;
        icmp_hdr->icmp_id = (unsigned short)GetCurrentProcessId();
        icmp_hdr->icmp_seq = i;
        icmp_hdr->icmp_timestamp = get_time_ms();
#else
        icmp_hdr = (struct icmp *)sendbuf;
        icmp_hdr->icmp_type = ICMP_ECHO;
        icmp_hdr->icmp_code = 0;
        icmp_hdr->icmp_id = pid & 0xFFFF;
        icmp_hdr->icmp_seq = i;
        
        // Store timestamp in data portion
        unsigned long timestamp = get_time_ms();
        memcpy(sendbuf + sizeof(struct icmp), &timestamp, sizeof(timestamp));
#endif

        memset(sendbuf + sizeof(*icmp_hdr) + sizeof(unsigned long), 'E', DEF_PACKET_SIZE - sizeof(unsigned long));
        
#ifdef _WIN32
        icmp_hdr->icmp_cksum = 0;
        icmp_hdr->icmp_cksum = checksum((unsigned short *)sendbuf, sizeof(ICMP_HDR) + DEF_PACKET_SIZE);
#else
        icmp_hdr->icmp_cksum = 0;
        icmp_hdr->icmp_cksum = checksum((unsigned short *)sendbuf, sizeof(struct icmp) + DEF_PACKET_SIZE);
#endif

        ret = sendto(sock, sendbuf, sizeof(*icmp_hdr) + DEF_PACKET_SIZE, 0, 
                    (struct sockaddr *)&dest, sizeof(dest));
        if (ret == SOCKET_ERROR) {
#ifdef _WIN32
            printf("sendto() failed: %d\n", WSAGetLastError());
#else
            perror("sendto");
#endif
            CLOSE_SOCKET(sock);
            return;
        }

        unsigned long send_time = get_time_ms();
        
        bread = recvfrom(sock, recvbuf, MAX_PACKET, 0, (struct sockaddr *)&from, &fromlen);
        if (bread == SOCKET_ERROR) {
#ifdef _WIN32
            if (WSAGetLastError() == WSAETIMEDOUT) {
                printf("Request timed out.\n");
                continue;
            }
            printf("recvfrom() failed: %d\n", WSAGetLastError());
#else
            perror("recvfrom");
#endif
            CLOSE_SOCKET(sock);
            return;
        }

#ifdef _WIN32
        PICMP_HDR recv_icmp_hdr = (PICMP_HDR)(recvbuf + 20); // IP header is 20 bytes
        if (recv_icmp_hdr->icmp_type == ICMP_ECHO_REPLY) {
            if (recv_icmp_hdr->icmp_id == (unsigned short)GetCurrentProcessId()) {
                inet_ntop(AF_INET, &from.sin_addr, ip_str, INET_ADDRSTRLEN);
                printf("Reply from %s: bytes=%d time=%ldms TTL=%d\n",
                       ip_str,
                       bread - 20 - sizeof(ICMP_HDR),
                       get_time_ms() - recv_icmp_hdr->icmp_timestamp,
                       recvbuf[8]); // TTL is at offset 8 in IP header
            }
        }
#else
        struct ip *ip_hdr = (struct ip *)recvbuf;
        int ip_hlen = ip_hdr->ip_hl << 2;
        struct icmp *recv_icmp_hdr = (struct icmp *)(recvbuf + ip_hlen);
        
        if (recv_icmp_hdr->icmp_type == ICMP_ECHOREPLY) {
            if (recv_icmp_hdr->icmp_id == (pid & 0xFFFF)) {
                unsigned long *timestamp_ptr = (unsigned long *)(recvbuf + ip_hlen + sizeof(struct icmp));
                unsigned long timestamp = *timestamp_ptr;
                
                inet_ntop(AF_INET, &from.sin_addr, ip_str, INET_ADDRSTRLEN);
                printf("Reply from %s: bytes=%d time=%ldms TTL=%d\n",
                       ip_str,
                       bread - ip_hlen - sizeof(struct icmp),
                       get_time_ms() - timestamp,
                       ip_hdr->ip_ttl);
            }
        }
#endif
        SLEEP_MS(1000);
    }
    CLOSE_SOCKET(sock);
}

void xnet_main(int argc, char **argv) {
#ifdef _WIN32
    WSADATA wsaData;
    int iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (iResult != 0) {
        printf("WSAStartup failed: %d\n", iResult);
        return;
    }
#endif

    if (argc > 1) {
        if (strcmp(argv[1], "show") == 0) {
            show_network_info();
        } else if (strcmp(argv[1], "ping") == 0) {
            if (argc > 2) {
                ping(argv[2]);
            } else {
                printf("xsh: xnet: ping requires a host\n");
            }
        } else if (strcmp(argv[1], "traceroute") == 0) {
            if (argc > 2) {
                printf("Traceroute not implemented in this version\n");
            } else {
                printf("xsh: xnet: traceroute requires a host\n");
            }
        } else {
            printf("xsh: xnet: unknown command '%s'\n", argv[1]);
        }
    } else {
        show_network_info();
    }

#ifdef _WIN32
    WSACleanup();
#endif
}
