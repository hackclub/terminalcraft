#include "clock.h"

long int get_time_in_usec(void) {
#if defined(WIN32) || defined(_WIN32) || defined(__WIN32__) || defined(__NT__)
#include <Windows.h>
    FILETIME ft;
    GetSystemTimeAsFileTime(&ft);
    unsigned long long tt = ft.dwHighDateTime;
    tt <<= 32;
    tt |= ft.dwLowDateTime;
    tt /= 10;
    tt -= 11644473600000000ULL;
#else
#include <sys/time.h>
    struct timeval tv;
    gettimeofday(&tv, 0);
    return tv.tv_usec;
#endif
}
