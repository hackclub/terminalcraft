#if PLATFORM_X11

#include "clipboard/x11/ClipboardListenerX11.hpp"

#include <unistd.h>
#include <xcb/xcb.h>
#include <xcb/xproto.h>

#include <cstdint>
#include <cstring>
#include <ctime>
#include <string>

#include "EventData.hpp"
#include "config.hpp"
#include "util.hpp"

namespace
{

xcb_atom_t getAtom(xcb_connection_t* connection, const std::string& name)
{
    xcb_intern_atom_cookie_t cookie = xcb_intern_atom(connection, 0, name.size(), name.c_str());
    xcb_intern_atom_reply_t* reply  = xcb_intern_atom_reply(connection, cookie, NULL);

    if (!reply)
        die("Failed to get atom with name \"{}\"", name);

    return reply->atom;
}

}  // namespace

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
    xcb_convert_selection(m_XCBConnection, m_Window, m_Clipboard, m_UTF8String, m_ClipboardProperty, XCB_CURRENT_TIME);
    xcb_flush(m_XCBConnection);

    xcb_generic_event_t* event;
    if ((event = xcb_wait_for_event(m_XCBConnection)))
    {
        xcb_get_property_cookie_t propertyCookie = xcb_get_property(m_XCBConnection, 0, m_Window, m_ClipboardProperty,
                                                                    XCB_GET_PROPERTY_TYPE_ANY, 0, UINT16_MAX);

        xcb_generic_error_t*      error         = nullptr;
        xcb_get_property_reply_t* propertyReply = xcb_get_property_reply(m_XCBConnection, propertyCookie, &error);

        if (error)
            die("Unknown libxcb error: {}", error->error_code);

        CopyEvent copyEvent{ reinterpret_cast<char*>(xcb_get_property_value(propertyReply)) };

        /* Simple but fine approach */
        if (copyEvent.content == m_LastClipboardContent)
            goto end;

        if (copyEvent.content.find_first_not_of(' ') == std::string::npos)
            goto end;

        if (copyEvent.content[0] == '\0')
        {
            std::string tmp{ copyEvent.content };
            copyEvent.content.clear();
            for (char c : tmp)
            {
                if (c != '\0')
                    copyEvent.content += c;
            }

            if (copyEvent.content == m_LastClipboardContent)
                goto end;
        }

        m_LastClipboardContent = copyEvent.content;
        for (const auto& callback : m_CopyEventCallbacks)
            callback(copyEvent);

    end:
        free(propertyReply);
    }

    free(event);
}

static void runInBg(xcb_connection_t* m_XCBConnection, xcb_atom_t target, xcb_atom_t property, const std::string& str)
{
    // handle selection requests in event loop
    xcb_generic_event_t* event;
    if ((event = xcb_wait_for_event(m_XCBConnection)))
    {
        if ((event->response_type & ~0x80) == XCB_SELECTION_REQUEST)
        {
            xcb_selection_request_event_t* request = reinterpret_cast<xcb_selection_request_event_t*>(event);
            if (request->target == target)
            {
                xcb_selection_notify_event_t notify_event = {};
                // setting the property
                xcb_change_property(m_XCBConnection, XCB_PROP_MODE_REPLACE, request->requestor, property, target, 8,
                                    str.size(), str.c_str());
                notify_event.response_type = XCB_SELECTION_NOTIFY;
                notify_event.requestor     = request->requestor;
                notify_event.selection     = request->selection;
                notify_event.target        = request->target;
                notify_event.property      = property;
                notify_event.time          = request->time;

                xcb_send_event(m_XCBConnection, false, request->requestor, XCB_EVENT_MASK_NO_EVENT,
                               reinterpret_cast<const char*>(&notify_event));
                xcb_flush(m_XCBConnection);
            }
        }
        free(event);
    }
}

void CClipboardListenerX11::CopyToClipboard(const std::string& str) const
{
    xcb_intern_atom_cookie_t cookie_selection = xcb_intern_atom(m_XCBConnection, 0, 9, "CLIPBOARD");
    xcb_intern_atom_cookie_t cookie_target    = xcb_intern_atom(m_XCBConnection, 0, 11, "UTF8_STRING");
    xcb_intern_atom_cookie_t cookie_property  = xcb_intern_atom(m_XCBConnection, 0, 8, "XCB_CLIPBOARD");

    xcb_intern_atom_reply_t* reply_selection = xcb_intern_atom_reply(m_XCBConnection, cookie_selection, NULL);
    xcb_intern_atom_reply_t* reply_target    = xcb_intern_atom_reply(m_XCBConnection, cookie_target, NULL);
    xcb_intern_atom_reply_t* reply_property  = xcb_intern_atom_reply(m_XCBConnection, cookie_property, NULL);

    if (!reply_selection || !reply_target || !reply_property)
    {
        free(reply_selection);
        free(reply_target);
        free(reply_property);
        die("Failed to get reply atoms");
    }

    xcb_atom_t selection = reply_selection->atom;
    xcb_atom_t target    = reply_target->atom;
    xcb_atom_t property  = reply_property->atom;

    free(reply_selection);
    free(reply_target);
    free(reply_property);

    // set our window as the selection owner
    xcb_set_selection_owner(m_XCBConnection, m_Window, selection, XCB_CURRENT_TIME);
    xcb_flush(m_XCBConnection);
    if (!config.silent)
        info("Copied to clipboard!");

    // run the task in the background, waiting for any event
    pid_t pid = fork();
    if (pid < 0)
        die("failed to fork(): {}", strerror(errno));
    else if (pid == 0)
        runInBg(m_XCBConnection, target, property, str);
    else
        exit(0);
}

#endif  // PLATFORM_X11
