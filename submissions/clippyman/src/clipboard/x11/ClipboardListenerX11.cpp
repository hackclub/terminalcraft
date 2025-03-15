#if PLATFORM_XORG

#include "clipboard/x11/ClipboardListenerX11.hpp"

#include <xcb/xcb.h>
#include <xcb/xproto.h>

#include <string>

#include "config.hpp"
#include "EventData.hpp"
#include "util.hpp"

xcb_atom_t getAtom(xcb_connection_t* connection, const std::string& name)
{
    xcb_intern_atom_cookie_t cookie = xcb_intern_atom(connection, 0, name.size(), name.c_str());
    xcb_intern_atom_reply_t* reply  = xcb_intern_atom_reply(connection, cookie, NULL);

    if (!reply)
        die("Failed to get atom with name \"{}\"", name);

    return reply->atom;
}

CClipboardListenerX11::CClipboardListenerX11()
{
    m_XCBConnection = xcb_connect(nullptr, nullptr);

    if (xcb_connection_has_error(m_XCBConnection) != 0)
        die("Failed to connect to X11 display!");

    const xcb_setup_t*          setup  = xcb_get_setup(m_XCBConnection);
    const xcb_screen_iterator_t iter   = xcb_setup_roots_iterator(setup);
    const xcb_screen_t*         screen = iter.data;

    if (!screen)
        die("Failed to get X11 root window!");

    m_Window = xcb_generate_id(m_XCBConnection);
    xcb_create_window(m_XCBConnection, XCB_COPY_FROM_PARENT, m_Window, screen->root, 0, 0, 1, 1, 0,
                      XCB_WINDOW_CLASS_INPUT_OUTPUT, screen->root_visual, 0, NULL);
    xcb_flush(m_XCBConnection);

    m_Clipboard         = getAtom(m_XCBConnection, config.primary_clip ? "PRIMARY" : "CLIPBOARD");
    m_UTF8String        = getAtom(m_XCBConnection, "UTF8_STRING");
    m_ClipboardProperty = getAtom(m_XCBConnection, "XCB_CLIPBOARD");
}

CClipboardListenerX11::~CClipboardListenerX11()
{
    if (m_XCBConnection)
        xcb_disconnect(m_XCBConnection);
}

/*
 * Registers a callback for when the user copies something.
 */
void CClipboardListenerX11::AddCopyCallback(const std::function<void(const CopyEvent&)>& func)
{
    m_CopyEventCallbacks.push_back(func);
}

void CClipboardListenerX11::PollClipboard()
{
    /* Request the clipboard contents */
    xcb_convert_selection(m_XCBConnection, m_Window, m_Clipboard, m_UTF8String, m_ClipboardProperty,
                          XCB_TIME_CURRENT_TIME);
    xcb_flush(m_XCBConnection);

    xcb_generic_event_t* event;
    if ((event = xcb_wait_for_event(m_XCBConnection)) != NULL)
    {
        xcb_get_property_cookie_t propertyCookie =
            xcb_get_property(m_XCBConnection, 0, m_Window, m_ClipboardProperty, XCB_GET_PROPERTY_TYPE_ANY, 0, 1024);

        xcb_generic_error_t*      error         = nullptr;
        xcb_get_property_reply_t* propertyReply = xcb_get_property_reply(m_XCBConnection, propertyCookie, &error);

        if (error)
            die("Unknown libxcb error: {}", error->error_code);

        std::string clipboardContent{reinterpret_cast<char*>(xcb_get_property_value(propertyReply))};

        /* Simple but fine approach */
        if (clipboardContent == m_LastClipboardContent)
            return;

        CopyEvent copyEvent{};
        copyEvent.content = clipboardContent;
        size_t pos = clipboardContent.find_first_not_of(' ');
        if (pos == clipboardContent.npos)
            return;

        for (const auto& callback : m_CopyEventCallbacks)
            callback(copyEvent);

        m_LastClipboardContent = clipboardContent;

        free(propertyReply);
        free(event);
    }
}

#endif  // PLATFORM_XORG
