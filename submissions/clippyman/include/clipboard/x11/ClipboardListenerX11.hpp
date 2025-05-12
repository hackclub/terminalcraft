#ifndef _CLIPBOARD_LISTENER_X11_HPP_
#define _CLIPBOARD_LISTENER_X11_HPP_

#if PLATFORM_X11

#include <xcb/xcb.h>
#include <xcb/xproto.h>

#include "clipboard/ClipboardListener.hpp"

class CClipboardListenerX11 : public CClipboardListener
{
public:
    CClipboardListenerX11();
    ~CClipboardListenerX11();

    void AddCopyCallback(const std::function<void(const CopyEvent&)>& func) override;

    void PollClipboard() override;

    void CopyToClipboard(const std::string& str) const override;

private:
    std::vector<std::function<void(const CopyEvent&)>> m_CopyEventCallbacks;

    xcb_connection_t* m_XCBConnection = nullptr;

    xcb_window_t m_Window;

    std::string m_LastClipboardContent;

    xcb_atom_t m_Clipboard, m_UTF8String, m_ClipboardProperty;
};

#endif  // PLATFORM_X11

#endif  // !CLIPBOARD_LISTENER_X11_HPP_
