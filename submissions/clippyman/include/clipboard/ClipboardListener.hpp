#ifndef CLIPBOARD_LISTENER_HPP_
#define CLIPBOARD_LISTENER_HPP_

#include <functional>

#include "EventData.hpp"
#include "config.hpp"
#include "util.hpp"

/* The base class for ClipboardListeners, Keep in mind this is not supposed to be used directly.
 * If you want a functional CClipboardListener instance, use GetAppropriateClipboardListener().
 */
class CClipboardListener
{
public:
    /*
     * Registers a callback for when the user copies something.
     */
    virtual void AddCopyCallback(const std::function<void(const CopyEvent&)>& func) = 0;

    /*
     * Poll for clipboard events, depending on the windowing system this MAY block.
     */
    virtual void PollClipboard() = 0;

    /*
     * Copy the content into the clipboard
     */
    virtual void CopyToClipboard(const std::string& str) const
    {
        if (!config.silent)
        {
#if !PLATFORM_X11
            warn("NOT yet implemented copy to clipboard in here, only X11.");
#endif
            info("Printing the selected content:");
        }
        fmt::print("{}", str);
        fmt::print("\n");
    }
};

#endif
