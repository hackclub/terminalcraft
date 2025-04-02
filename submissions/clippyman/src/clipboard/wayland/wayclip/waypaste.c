#define _POSIX_C_SOURCE 200809L

#include <stdbool.h>
#include <string.h>
#include <wayland-client.h>
#include <unistd.h>

#include "protocol/wlr-data-control-unstable-v1-client-protocol.h"
#include "common.h"

struct wl_display *g_display;
struct zwlr_data_control_offer_v1 *acceptedoffer = NULL;
int g_fd;
int pipes[2];

static void
receive(int cond, struct zwlr_data_control_offer_v1 *offer)
{
	if (cond && acceptedoffer == offer) {
		zwlr_data_control_offer_v1_receive(offer, options.type, pipes[1]);
		wl_display_roundtrip(g_display);
		close(pipes[1]);
                ftruncate(g_fd, 0);

		copyfd(pipes[0], g_fd);
		close(pipes[0]);

		if (pipe(pipes) == -1)
			wc_die("failed to create pipe");

		// exit(0);
	}

	if (acceptedoffer)
		zwlr_data_control_offer_v1_destroy(acceptedoffer);

	acceptedoffer = NULL;
}

void
offer_offer(void *data, struct zwlr_data_control_offer_v1 *offer, const char *mime_type)
{
	if (acceptedoffer)
		return;

	if (strcmp(mime_type, options.type) == 0)
		acceptedoffer = offer;
}

static const struct zwlr_data_control_offer_v1_listener offer_listener = {
	.offer = offer_offer,
};

void
control_data_offer(void *data, struct zwlr_data_control_device_v1 *device, struct zwlr_data_control_offer_v1 *offer)
{
	zwlr_data_control_offer_v1_add_listener(offer, &offer_listener, NULL);
}

void
control_data_selection(void *data, struct zwlr_data_control_device_v1 *device, struct zwlr_data_control_offer_v1 *offer)
{
	if (offer)
		receive(!options.primary, offer);
}

void
control_data_primary_selection(void *data, struct zwlr_data_control_device_v1 *device, struct zwlr_data_control_offer_v1 *offer)
{
	if (offer)
		receive(options.primary, offer);
}

static const struct zwlr_data_control_device_v1_listener device_listener = {
	.data_offer = control_data_offer,
	.selection = control_data_selection,
	.primary_selection = control_data_primary_selection,
};

void
main_waypaste(struct wl_display *display, const int fd)
{
        g_display = display;
        g_fd = fd;

        struct wl_registry *const registry = wl_display_get_registry(display);
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

	if (pipe(pipes) == -1)
		wc_die("failed to create pipe");

	struct zwlr_data_control_device_v1 *device = zwlr_data_control_manager_v1_get_data_device(data_control_manager, seat);
	if (device == NULL)
		wc_die("data device is null");

	zwlr_data_control_device_v1_add_listener(device, &device_listener, NULL);
}

// vim:shiftwidth=8
