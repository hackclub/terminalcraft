#ifndef _CLIPBOARD_LISTENER_WAYLAND_HPP_
#define _CLIPBOARD_LISTENER_WAYLAND_HPP_

#if PLATFORM_WAYLAND

#include <string>
#include <vector>

#include "clipboard/ClipboardListener.hpp"

extern "C" {
    #include "clipboard/wayland/wayclip/common.h"
    #include <wayland-client.h>
    #include <wayland-client-protocol.h>
}

class CClipboardListenerWayland : public CClipboardListener
{
public:
    CClipboardListenerWayland(const wc_options& options);
    ~CClipboardListenerWayland();

    void AddCopyCallback(const std::function<void(const CopyEvent&)>& func) override;
    void PollClipboard() override;

private:

    std::vector<std::function<void(const CopyEvent&)>> m_CopyEventCallbacks;

    wl_display* m_display = nullptr;

    std::string m_path{"/tmp"};

    const wc_options& m_options;

    unsigned int m_lastModifiedFileTime = 0;

    std::string m_LastClipboardContent;
};

#endif  // PLATFORM_WAYLAND

#endif  // !_CLIPBOARD_LISTENER_WAYLAND_HPP_
