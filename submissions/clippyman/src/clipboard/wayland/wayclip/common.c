#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <wayland-client.h>

#include "protocol/wlr-data-control-unstable-v1-client-protocol.h"
#include "common.h"

static bool seat_found = false;

struct wl_seat *seat;
struct zwlr_data_control_manager_v1 *data_control_manager;

struct options options = {
	.type = "text/plain;charset=utf-8",
        //.seat = "seat0"
};

static void
seat_capabilities(void *data, struct wl_seat *seat, uint32_t cap)
{
}

static void
seat_name(void *data, struct wl_seat *_seat, const char *name)
{
	if (!seat_found && strcmp(name, options.seat) == 0) {
		seat_found = true;
		seat = _seat;
	} else wl_seat_destroy(_seat);
}

static const struct wl_seat_listener seat_listener = {
	.capabilities = seat_capabilities,
	.name = seat_name,
};

void
registry_global(void *data, struct wl_registry *registry, uint32_t name, const char *interface, uint32_t version)
{
	if (!seat_found && strcmp(interface, "wl_seat") == 0) {
		seat = wl_registry_bind(registry, name, &wl_seat_interface, 2);
		if (options.seat) {
			wl_seat_add_listener(seat, &seat_listener, NULL);
			seat = NULL;
		} else seat_found = true;
	} else if (strcmp(interface, "zwlr_data_control_manager_v1") == 0) {
		data_control_manager = wl_registry_bind(registry, name, &zwlr_data_control_manager_v1_interface, 2);
	}
}

void
registry_global_remove(void *data, struct wl_registry *registry, uint32_t name)
{
}

const struct wl_registry_listener registry_listener = {
	.global = registry_global,
	.global_remove = registry_global_remove,
};

void
wc_die(const char *const error)
{
	fprintf(stderr, "wayclip: %s\n", error);
	exit(1);
}

void
wc_warn(const char *const error)
{
	fprintf(stderr, "wayclip: warning: %s\n", error);
}

void
copyfd(const int in, const int out)
{
	char buf[BUFSIZ];

	do {
		ssize_t rcount = read(in, buf, BUFSIZ);
		if (rcount == -1) {
			wc_warn("read failed");
			return;
		}

		size_t wcount = 0;
		char *ptr = buf;
		while (wcount < rcount) {
			ssize_t len = write(out, ptr, rcount);
			if (len == -1) {
				wc_warn("read failed");
				return;
			}

			ptr += len;
			wcount += len;
		}
		if (!rcount)
			break;
	} while (1);
}
