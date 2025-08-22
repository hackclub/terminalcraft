#define _POSIX_C_SOURCE 200809L

#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <wayland-client.h>
#include <unistd.h>

#include "protocol/wlr-data-control-unstable-v1-client-protocol.h"
#include "common.h"

struct wl_registry *registry;
int temp;

bool running = true;

void
data_source_send(void *data, struct zwlr_data_control_source_v1 *source, const char *mime_type, int32_t fd)
{
	lseek(temp, 0, SEEK_SET);

	copyfd(fd, temp);
	close(fd);
}

void
data_source_cancelled(void *data, struct zwlr_data_control_source_v1 *source)
{
	running = 0;
}

static const struct zwlr_data_control_source_v1_listener data_source_listener = {
	.send = data_source_send,
	.cancelled = data_source_cancelled,
};

const char *const tempname = "/waycopy-buffer-XXXXXX";

int
main_waycopy(struct wl_display *display, struct wc_options options, const int fd)
{
	char path[PATH_MAX] = {0};
	char *ptr = getenv("TMPDIR");
	if (ptr == NULL)
		strcpy(path, "/tmp");
	else {
		if (strlen(ptr) > PATH_MAX - strlen(tempname))
			wc_die("TMPDIR has too long of a path");

		strcpy(path, ptr);
	}

	strncat(path, tempname, PATH_MAX - 1);
	temp = mkstemp(path);
	if (temp == -1)
		wc_die("failed to create temporary file for copy buffer");

	if (unlink(path) == -1)
		wc_die("failed to remove temporary file");
	copyfd(fd, temp);
	close(fd);

        registry = wl_display_get_registry(display);
	if (registry == NULL)
		wc_die("failed to get registry");

	wl_registry_add_listener(registry, &registry_listener, NULL);

	wl_display_roundtrip(display);
	if (options.seat)
		wl_display_roundtrip(display);

	if (seat == NULL)
		wc_die("failed to bind to seat interface");

	if (data_control_manager == NULL)
		wc_die("failed to bind to data_control_manager interface\n"
                        "Looks like you are using GNOME/KDE or a compositor that doesn't have the interface \"zwlr_data_control_manager_v1\"\n"
                        "Please either use 'clippyman' or 'clippyman-x11' if you have Xwayland working.\n"
                        "If not, just install 'wl-clipboard' and pipe the clipboard like \"wl-paste | clippyman -i\"");

	struct zwlr_data_control_device_v1 *device = zwlr_data_control_manager_v1_get_data_device(data_control_manager, seat);
	if (device == NULL)
		wc_die("data device is null");

	struct zwlr_data_control_source_v1 *source = zwlr_data_control_manager_v1_create_data_source(data_control_manager);
	if (source == NULL)
		wc_die("source is null");

	zwlr_data_control_source_v1_offer(source, options.type);
	zwlr_data_control_source_v1_add_listener(source, &data_source_listener, NULL);

	if (options.primary)
		zwlr_data_control_device_v1_set_primary_selection(device, source);
	else
		zwlr_data_control_device_v1_set_selection(device, source);

	return running;
}

// vim:shiftwidth=8
