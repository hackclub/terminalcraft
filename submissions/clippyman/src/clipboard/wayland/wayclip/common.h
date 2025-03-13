#ifndef _WAYCLIP_SRC_COMMON_H_
#define _WAYCLIP_SRC_COMMON_H_

#include <stdbool.h>
#include <wayland-client.h>

#pragma GCC diagnostic ignored "-Wunused-parameter"

extern struct wl_seat *seat;
extern struct zwlr_data_control_manager_v1 *data_control_manager;
extern const struct wl_registry_listener registry_listener;

extern struct options {
	const char *type;
	const char *seat;
	bool foreground;
	bool primary;
} options;

void wc_die(const char *const error);
void wc_warn(const char *const error);
void copyfd(int in, int out);

int main_waycopy(struct wl_display *display, struct options options);
void main_waypaste(struct wl_display *display, const int fd);

#endif // !_WAYCLIP_SRC_COMMON_H_
