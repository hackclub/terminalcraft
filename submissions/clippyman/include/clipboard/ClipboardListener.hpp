#ifndef CLIPBOARD_LISTENER_HPP_
#define CLIPBOARD_LISTENER_HPP_

#include <functional>

#include "EventData.hpp"

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
};

#endif
